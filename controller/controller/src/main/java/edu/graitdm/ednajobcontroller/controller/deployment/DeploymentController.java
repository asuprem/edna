package edu.graitdm.ednajobcontroller.controller.deployment;

import edu.graitdm.ednajobcontroller.events.GenericEventQueueConsumer;

import io.fabric8.kubernetes.api.model.apps.Deployment;
import io.fabric8.kubernetes.client.KubernetesClient;
import org.microbean.kubernetes.controller.AbstractEvent;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import org.microbean.kubernetes.controller.Controller;

import java.io.IOException;

/**
 * <code>DeploymentController</code> manages new deployments that
 * {@link edu.graitdm.ednajobcontroller.controller.ednajob.EdnaJobController} generates for an <code>EdnaJob</code>
 * custom resource. When starting, <code>DeploymentController</code> will also record existing deployments
 * in kubernetes.
 */
public class DeploymentController extends GenericEventQueueConsumer<Deployment> {

    private static final Logger LOGGER = LoggerFactory.getLogger(DeploymentController.class.getSimpleName());
    private final Controller<Deployment> controller;

    /**
     * Constructor for <code>DeploymentController</code>.
     *
     * @param client A {@link KubernetesClient} instance to communicate with the kube api-server.
     * @param deploymentStore A {@link DeploymentStore} instance to store references to existing and new
     *                        kubernetes deployments.
     */
    public DeploymentController(KubernetesClient client, DeploymentStore deploymentStore){
        // Call constructor in GenericEventQueueConsumer
        // GenericEventQueueConsumer, in turn, calls the constructor on deploymentStore, and sets up
        // its event listeners (we don't need these for now) plus the class name.
        super(deploymentStore);
        //  Instantiate the controller.
        controller = new Controller<>(client.apps().deployments().inAnyNamespace(), this);
    }

    /**
     * Method triggers when a deployment is added to Kubernetes.
     *
     * @param event Wraps around the resource that has been added. event.getCurrentResource() gets the specific
     *              resource that's added.
     */
    @Override
    public void onAddition(AbstractEvent<? extends Deployment> event) {
        LOGGER.info("Added deployment for: {}", event.getResource().getMetadata().getName());
    }

    /**
     * Method triggers when a deployment is modified in Kubernetes.
     *
     * @param event Wraps around the resource that has been modified. event.getCurrentResource() gets the specific
     *              resource that's modified. event.getPriorResource() gets the resource before it was modified
     */
    @Override
    public void onModification(AbstractEvent<? extends Deployment> event) {
        LOGGER.info("Modified deployment for: {}", event.getResource().getMetadata().getName());
    }

    /**
     * Method triggers when a deployment is deleted in Kubernetes.
     *
     * @param event Wraps around the resource that has been deleted. event.getCurrentResource() gets the specific
     *              resource that's deleted.
     */
    @Override
    public void onDeletion(AbstractEvent<? extends Deployment> event) {
        LOGGER.info("Deleted deployment for: {}", event.getResource().getMetadata().getName());
    }

    /**
     * Starts the controller.
     *
     * @throws IOException
     */
    public void start() throws IOException {
        controller.start();
    }

    /**
     * Shuts down the controller.
     *
     * @throws IOException
     */
    public void close() throws IOException {
        controller.close();
    }
}

