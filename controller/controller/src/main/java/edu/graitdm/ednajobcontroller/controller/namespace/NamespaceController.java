package edu.graitdm.ednajobcontroller.controller.namespace;

import edu.graitdm.ednajobcontroller.events.GenericEventQueueConsumer;

import io.fabric8.kubernetes.api.model.Namespace;
import io.fabric8.kubernetes.client.KubernetesClient;
import org.microbean.kubernetes.controller.AbstractEvent;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

// We use this for type specificity, because the
// io.fabric8.kubernetes.api.Controller does not specify the controller type.
import org.microbean.kubernetes.controller.Controller;

import java.io.IOException;



public class NamespaceController extends GenericEventQueueConsumer<Namespace> {
    // Get the class name for the logger
    private static final Logger LOGGER = LoggerFactory.getLogger(NamespaceController.class.getSimpleName());

    // Initialize the controller
    private final Controller<Namespace> controller;

    public NamespaceController(KubernetesClient client, NamespaceStore namespaceStore){
        // This calls the constructor in GenericEventQueueConsumer that takes in a ConcurrentHashMap
        // GenericEventQueueConsumer, in turn, calls the constructor on deploymentStore, and sets up
        // its event listeners (we don't need these for now) plus the class name.
        super(namespaceStore);
        //  Instantiate the controller.
        controller = new Controller<>(client.namespaces(), this);
    }


    @Override
    public void onAddition(AbstractEvent<? extends Namespace> event) {
        LOGGER.info("Added namespace for: {}", event.getResource().getMetadata().getName());
    }

    @Override
    public void onModification(AbstractEvent<? extends Namespace> event) {
        LOGGER.debug("Modified namespace for: {}", event.getResource().getMetadata().getName());
    }

    @Override
    public void onDeletion(AbstractEvent<? extends Namespace> event) {
        LOGGER.info("Deleted namespace for: {}", event.getResource().getMetadata().getName());
    }


    public void start() throws IOException {
        controller.start();
    }

    public void close() throws IOException {
        controller.close();
    }
}

