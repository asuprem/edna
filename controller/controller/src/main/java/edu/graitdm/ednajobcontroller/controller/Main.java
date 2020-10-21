package edu.graitdm.ednajobcontroller.controller;

import edu.graitdm.ednajobcontroller.controller.deployment.DeploymentController;
import edu.graitdm.ednajobcontroller.controller.deployment.DeploymentFactory;
import edu.graitdm.ednajobcontroller.controller.deployment.DeploymentStore;
import edu.graitdm.ednajobcontroller.controller.ednajob.EdnaJobController;
import edu.graitdm.ednajobcontroller.controller.ednajob.EdnaJobFactory;
import edu.graitdm.ednajobcontroller.controller.ednajob.EdnaJobStore;
import io.fabric8.kubernetes.client.*;
import org.apache.log4j.BasicConfigurator;
import org.slf4j.bridge.SLF4JBridgeHandler;

import java.io.IOException;
import java.util.Optional;
import java.util.concurrent.locks.Condition;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

import org.apache.log4j.Level;
import org.apache.log4j.LogManager;
import org.apache.log4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.bridge.SLF4JBridgeHandler;

public class Main {
    private static final Lock lock = new ReentrantLock();
    private static final Condition terminated = lock.newCondition();

    public static void main(String[] args) {
        BasicConfigurator.configure();
        /*
         * Register a shutdown hook. When shutdown occurs, this thread signals the terminated condition.
         */
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            lock.lock();
            terminated.signal();
            lock.unlock();
        }));

        /*
         * Send JUL log events to SLF4J.
         */
        SLF4JBridgeHandler.removeHandlersForRootLogger();
        SLF4JBridgeHandler.install();

        /*
         * Set the JUL loggers' to the minimum verbosity.
         */
        var juls = java.util.logging.LogManager.getLogManager().getLoggerNames();
        while (juls.hasMoreElements()) {
            var logger = java.util.logging.Logger.getLogger(juls.nextElement());
            logger.setLevel(java.util.logging.Level.OFF);
        }

        /*
         * Main try block.
         */
        try {
            var logLevel = Optional.ofNullable(System.getenv("LOG_LEVEL")).orElse("DEBUG");
            var loggers = LogManager.getCurrentLoggers();
            while(loggers.hasMoreElements()) {
                Logger logger = (Logger) loggers.nextElement();
                logger.setLevel(Level.toLevel(logLevel));
            }

            org.slf4j.Logger LOGGER;
            LOGGER = LoggerFactory.getLogger(Main.class);
            LOGGER.info("Entered Main");

            // Set up the namespace. This is the namespace for the EdnaJobs
            // VERY IMPORTANT -- the deployments for a job exist in a different namespace
            // All EdnaJobs exist in the default namespace
            // The generated deployments exist in a new namespace named after the application for the EdnaJob
            // We will have to create the namespace if it does not exist, by the way...
            // We will also have to delete the namespace if we delete all jobs for that application...
            var ns = Optional.ofNullable(System.getenv("EDNAJOB_NAMESPACE")).orElse("default");

            /*
             * Grab a new Kube client.
             */
            // TODO (Abhijit) fix this hacky workaround.
            String url = "http://127.0.0.1:8080";
            /*Config config = new ConfigBuilder()
                    .withCaCertData(caCert)
                    .withOauthToken(token)
                    .withMasterUrl(url)
                    .build();
            */

            var client = new DefaultKubernetesClient(url);
            LOGGER.info("Created Kubernetes client");



            // This stores the edna jobs we have applied. We can use this to fetch the resource associated with a name
            var ednaJobStore = new EdnaJobStore();
            // This is basically for updates. Essentially, when we update an existing custom resource, we use
            // the update method in the factory to patch the resource in memory;
            // In turn, this triggers onUpdate().
            var ednaJobFactory = new EdnaJobFactory(client);



            // This stores the deployments we have applied. We can use this to fetch a deployment associated with an EdnaJob
            // by using the EdnaJob name.
            // NOTE: When we create the deployment, we MUST create a label for it where EJ_NAME_KEY=ednajob.metadata.name
            var deploymentStore = new DeploymentStore();
            // This is what actually creates the deployments for a job.
            // TODO add dockerStore, dockerFactory, dockerController?
            var deploymentFactory = new DeploymentFactory(client, deploymentStore, ednaJobFactory);
            var deploymentController = new DeploymentController(client, deploymentStore, ns);



            var ednaJobController = new EdnaJobController(client,
                                        ednaJobStore, ednaJobFactory,
                                        deploymentFactory, deploymentStore,
                                        ns);



            /*
             * Start the Job FSM and the controllers
             */
            lock.lock();
            ednaJobController.start();
            deploymentController.start();
            terminated.await(); // Here, the shutdown hook will trigger this signal
            lock.unlock();

            // Close the controllers
            ednaJobController.close();
            deploymentController.close();

        } catch (KubernetesClientException | InterruptedException | IOException e) {
            e.printStackTrace();
        }


    }
}
