package edu.graitdm.ednajobcontroller.controller;


import com.beust.jcommander.JCommander;
import edu.graitdm.ednajobcontroller.configuration.BaseConfiguration;

import edu.graitdm.ednajobcontroller.controller.docker.DockerFactory;
import edu.graitdm.ednajobcontroller.controller.namespace.NamespaceController;
import edu.graitdm.ednajobcontroller.controller.namespace.NamespaceFactory;
import edu.graitdm.ednajobcontroller.controller.namespace.NamespaceStore;

import edu.graitdm.ednajobcontroller.controller.deployment.DeploymentController;
import edu.graitdm.ednajobcontroller.controller.deployment.DeploymentFactory;
import edu.graitdm.ednajobcontroller.controller.deployment.DeploymentStore;

import edu.graitdm.ednajobcontroller.controller.ednajob.EdnaJobController;
import edu.graitdm.ednajobcontroller.controller.ednajob.EdnaJobFactory;
import edu.graitdm.ednajobcontroller.controller.ednajob.EdnaJobStore;

import com.github.dockerjava.core.DefaultDockerClientConfig;
import com.github.dockerjava.core.DockerClientConfig;
import com.github.dockerjava.api.DockerClient;
import com.github.dockerjava.core.DockerClientImpl;
import com.github.dockerjava.httpclient5.ApacheDockerHttpClient;
import com.github.dockerjava.transport.DockerHttpClient;



import io.fabric8.kubernetes.client.DefaultKubernetesClient;
import io.fabric8.kubernetes.client.KubernetesClientException;
import org.apache.log4j.BasicConfigurator;
import org.apache.log4j.Level;
import org.apache.log4j.LogManager;
import org.apache.log4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.bridge.SLF4JBridgeHandler;

import java.io.IOException;
import java.util.Optional;
import java.util.concurrent.locks.Condition;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;


/**
 * Entrypoint to the controller.
 */
public class Main {
    private static final Lock lock = new ReentrantLock();
    private static final Condition terminated = lock.newCondition();

    /**
     * Entrypoint to the controller
     *
     * @param args  The command line arguments for the controller
     *
     */
    public static void main(String[] args) {
        BasicConfigurator.configure();  // Logger

        /**
         * Register a shutdown hook. When shutdown occurs, this thread signals the terminated condition.
         */
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            lock.lock();
            terminated.signal();
            lock.unlock();
        }));

        /**
         * Send JUL log events to SLF4J.
         */
        SLF4JBridgeHandler.removeHandlersForRootLogger();
        SLF4JBridgeHandler.install();

        /**
         * Set the JUL loggers' to the minimum verbosity.
         */
        var juls = java.util.logging.LogManager.getLogManager().getLoggerNames();
        while (juls.hasMoreElements()) {
            var logger = java.util.logging.Logger.getLogger(juls.nextElement());
            logger.setLevel(java.util.logging.Level.OFF);
        }

        /**
         * Main try block for controller
         */
        try {
            // Set up Loggers
            var logLevel = Optional.ofNullable(System.getenv("LOG_LEVEL")).orElse("DEBUG");
            var loggers = LogManager.getCurrentLoggers();
            while(loggers.hasMoreElements()) {
                Logger logger = (Logger) loggers.nextElement();
                logger.setLevel(Level.toLevel(logLevel));
            }
            org.slf4j.Logger LOGGER;
            LOGGER = LoggerFactory.getLogger(Main.class);
            LOGGER.info("Starting the controller...");

            /**
             * Set up the command line configuration options
             */
            BaseConfiguration configuration = new BaseConfiguration();
            JCommander.newBuilder().addObject(configuration).build().parse(args);

            // Namespace for the controller
            var ns = configuration.getEdnaNamespace();


            /**
             * Grab a new Kube client.
             */
            // TODO (Abhijit) fix this hacky workaround.
            var client = new DefaultKubernetesClient(configuration.getKubectlURL());
            LOGGER.info("Created Kubernetes client connected to {}", configuration.getKubectlURL());


            /**
             * Set up the controller's Store and Factory to store and generate new EdnaJob resources
             */
            var ednaJobStore = new EdnaJobStore();
            var ednaJobFactory = new EdnaJobFactory(client);

            /**
             * Set up the DeploymentController's Store and Factory, then pass them to the DeploymentController
             */
            var deploymentStore = new DeploymentStore();
            var deploymentFactory = new DeploymentFactory(client, deploymentStore, ednaJobFactory);
            var deploymentController = new DeploymentController(client, deploymentStore);

            /**
             * Set up the NamespaceController's Store and Factory, then pass them to the NamespaceController
             */
            var namespaceStore = new NamespaceStore();
            var namespaceFactory = new NamespaceFactory(client, namespaceStore,deploymentStore);
            var namespaceController = new NamespaceController(client,namespaceStore);

            /**
             * Set up the Docker client
             */
            DockerClientConfig dockerConfig = DefaultDockerClientConfig.createDefaultConfigBuilder()
                        .withDockerHost(configuration.getDockerHost())
                        .build();
            DockerHttpClient httpClient = new ApacheDockerHttpClient.Builder()
                                    .dockerHost(dockerConfig.getDockerHost())
                                    .sslConfig(dockerConfig.getSSLConfig())
                                    .build();
            DockerClient dockerClient = DockerClientImpl.getInstance(dockerConfig, httpClient);
            var dockerFactory = new DockerFactory(dockerClient, configuration);
            /**
             * Set up the EdnaJobController
             */
            var ednaJobController = new EdnaJobController(client,
                                        ednaJobStore, ednaJobFactory,
                                        deploymentFactory, deploymentStore,
                                        namespaceFactory, namespaceStore,
                                        dockerFactory,
                                        ns);

            /*
             * Start the EdnaJob FSM and the sub-controllers
             */
            lock.lock();
            ednaJobController.start();
            deploymentController.start();
            namespaceController.start();
            terminated.await(); // Here, the shutdown hook from earlier will trigger this signal
            lock.unlock();

            // Close the controllers
            ednaJobController.close();
            deploymentController.close();
            namespaceController.close();

        } catch (KubernetesClientException | InterruptedException | IOException e) {
            e.printStackTrace();
        }


    }
}
