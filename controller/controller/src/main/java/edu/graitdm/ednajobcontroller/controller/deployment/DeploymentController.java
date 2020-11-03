package edu.graitdm.ednajobcontroller.controller.deployment;

import edu.graitdm.ednajobcontroller.events.GenericEventQueueConsumer;

import io.fabric8.kubernetes.api.model.apps.Deployment;
import io.fabric8.kubernetes.client.KubernetesClient;
import org.microbean.kubernetes.controller.AbstractEvent;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

// We use this for type specificity, because the
// io.fabric8.kubernetes.api.Controller does not specify the controller type.
import org.microbean.kubernetes.controller.Controller;

import java.io.IOException;

public class DeploymentController extends GenericEventQueueConsumer<Deployment> {
    // Get the class name for the logger
    private static final Logger LOGGER = LoggerFactory.getLogger(DeploymentController.class);

    // Initialize the controller
    private final Controller<Deployment> controller;

    public DeploymentController(KubernetesClient client, DeploymentStore deploymentStore){
        // This calls the constructor in GenericEventQueueConsumer that takes in a ConcurrentHashMap
        // GenericEventQueueConsumer, in turn, calls the constructor on deploymentStore, and sets up
        // its event listeners (we don't need these for now) plus the class name.
        super(deploymentStore);
        //  Instantiate the controller.
        controller = new Controller<>(client.apps().deployments().inAnyNamespace(), this);
    }


    @Override
    public void onAddition(AbstractEvent<? extends Deployment> event) {
        LOGGER.info("Added deployment for: {}", event.getResource().getMetadata().getName());
    }

    @Override
    public void onModification(AbstractEvent<? extends Deployment> event) {
        LOGGER.info("Modified deployment for: {}", event.getResource().getMetadata().getName());
    }

    @Override
    public void onDeletion(AbstractEvent<? extends Deployment> event) {
        LOGGER.info("Deleted deployment for: {}", event.getResource().getMetadata().getName());
    }


    public void start() throws IOException {
        controller.start();
    }

    public void close() throws IOException {
        controller.close();
    }
}

