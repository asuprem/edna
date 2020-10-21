package edu.graitdm.ednajobcontroller.controller.ednajob;

import edu.graitdm.ednajobcontroller.controller.deployment.DeploymentFactory;
import edu.graitdm.ednajobcontroller.controller.deployment.DeploymentStore;
import edu.graitdm.ednajobcontroller.events.GenericEventQueueConsumer;
import io.fabric8.kubernetes.client.KubernetesClient;
import org.microbean.kubernetes.controller.AbstractEvent;
import org.microbean.kubernetes.controller.Controller;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;

public class EdnaJobController extends GenericEventQueueConsumer<EdnaJob> {
    private static final Logger LOGGER = LoggerFactory.getLogger(EdnaJobController.class);

    private final EdnaJobFactory ednaJobFactory;
    private final DeploymentFactory deploymentFactory;
    private final DeploymentStore deploymentStore;
    // TODO maybe add the docker store and factory here?

    private final Controller<EdnaJob> controller;

    public EdnaJobController(KubernetesClient client, EdnaJobStore ednaJobStore, EdnaJobFactory ednaJobFactory,
                             DeploymentFactory deploymentFactory, DeploymentStore deploymentStore,
                             String ns){
        super(ednaJobStore);
        this.ednaJobFactory = ednaJobFactory;
        this.deploymentStore = deploymentStore;
        this.deploymentFactory = deploymentFactory;
        var customResourceImpl = client.customResources(ednaJobFactory.getCustomResourceDefinition(),
        EdnaJob.class,
                EdnaJobList.class,
                EdnaJobDoneable.class).inNamespace(ns);
        this.controller = new Controller<>(
                customResourceImpl, this);

    }


    @Override
    public void onAddition(AbstractEvent<? extends EdnaJob> event) {
        LOGGER.info("ADD EdnaJob - {}", event.getResource().getMetadata().getName());
        ednaJobFactory.update(event.getResource(), EEdnaJobState.DEPLOYMENT_CREATION);
    }

    @Override
    public void onModification(AbstractEvent<? extends EdnaJob> event) {
        // A modification is triggered, so we get the prior and current resource...
        LOGGER.info("MOD EdnaJob - {}", event.getResource().getMetadata().getName());
        var priorResource = event.getPriorResource();
        var currentResource = event.getResource();


        // TODO This is where we do operations for each of our states in EEdnaJobState
        switch(currentResource.getSpec().getState()){
            case UNDEFINED:
                LOGGER.info("MOD - Invalid transition to Undefined -- {}", event.getResource().getMetadata().getName());
                break;
            case DEPLOYMENT_CREATION:
                LOGGER.info("MOD - DEPLOYMENT_CREATION -- {}", event.getResource().getMetadata().getName());
                // TODO  So we need to update the add() method to create a deployment given the currentResource,
                //  which is an applied EdnaJob
                deploymentFactory.add(currentResource);
                break;
            case DEPLOYMENT_DELETION:
                //TODO (Abhijit) We will never get this state, because the ednajob's already deleted...so fix this
                LOGGER.info("MOD - DEPLOYMENT_DELETION -- {}", event.getResource().getMetadata().getName());
                break;
            case READY:
                // TODO (Abhijit) is this state every reached???
                LOGGER.info("MOD - READY -- {}", event.getResource().getMetadata().getName());
                break;

        }



    }

    @Override
    public void onDeletion(AbstractEvent<? extends EdnaJob> event) {
        LOGGER.info("DEL EdnaJob - {}", event.getResource().getMetadata().getName());
        ednaJobFactory.update(event.getResource(), EEdnaJobState.DEPLOYMENT_DELETION);
        // TODO (Abhijit) delete deployment here...and verify this works
        var deployments = deploymentStore.getDeploymentsforEdnaJob(event.getResource());
        deployments.forEach(target -> {
            deploymentFactory.delete(target);
        });
    }

    public void start() throws IOException {
        controller.start();
    }

    public void close() throws IOException {
        controller.close();
    }
}
