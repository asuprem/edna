package edu.graitdm.ednajobcontroller.controller.deployment;

import edu.graitdm.ednajobcontroller.controller.ednajob.EdnaJob;
import edu.graitdm.ednajobcontroller.controller.ednajob.EdnaJobFactory;

import io.fabric8.kubernetes.api.model.Container;
import io.fabric8.kubernetes.api.model.LabelSelector;
import io.fabric8.kubernetes.api.model.ObjectMeta;
import io.fabric8.kubernetes.api.model.OwnerReference;
import io.fabric8.kubernetes.api.model.PodSpec;
import io.fabric8.kubernetes.api.model.PodTemplateSpec;
import io.fabric8.kubernetes.api.model.apiextensions.CustomResourceDefinition;
import io.fabric8.kubernetes.api.model.apps.Deployment;
import io.fabric8.kubernetes.api.model.apps.DeploymentBuilder;
import io.fabric8.kubernetes.api.model.apps.DeploymentSpec;
import io.fabric8.kubernetes.client.KubernetesClient;
import io.fabric8.openshift.api.model.Template;
import org.apache.commons.lang.RandomStringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Collections;
import java.util.HashMap;

import static edu.graitdm.ednajobcontroller.controller.ICustomResourceCommons.EJ_API_VERSION;
import static edu.graitdm.ednajobcontroller.controller.ICustomResourceCommons.EJ_APP_LABEL_KEY;
import static edu.graitdm.ednajobcontroller.controller.ICustomResourceCommons.EJ_APP_LABEL_VALUE;
import static edu.graitdm.ednajobcontroller.controller.ICustomResourceCommons.EJ_KIND_NAME;
import static edu.graitdm.ednajobcontroller.controller.ICustomResourceCommons.EJ_NAME_KEY;

public class DeploymentFactory {

    private static final Logger LOGGER = LoggerFactory.getLogger(DeploymentFactory.class);

    private final KubernetesClient client;
    private final DeploymentStore deploymentStore;
    private final EdnaJobFactory ednaJobFactory;

    // Constructor
    public DeploymentFactory(KubernetesClient client, DeploymentStore deploymentStore, EdnaJobFactory ednaJobFactory){
        this.client = client;
        this.deploymentStore = deploymentStore;
        this.ednaJobFactory = ednaJobFactory;
    }

    //Basically make sure the deployment we are, well, deploying, has a unique name.
    public boolean isUnique(String name){
        return deploymentStore.values().stream().noneMatch(deployment -> deployment.getMetadata().getName().equals(name));
    }

    // Given a custom resource, get a unique name for the deployment by attaching a random suffix to the base name
    // TODO we should not need this...
    private String getUniqueDeploymentName(EdnaJob ednaJob){
        String deploymentName;
        do{
            var suffix = RandomStringUtils.random(5,true,true).toLowerCase();
            deploymentName = ednaJob.getMetadata().getName() + "-" + suffix;
        } while(!isUnique(deploymentName));
        return deploymentName;
    }

    public void add(EdnaJob ednaJob){
        /*
         * Log the add
         */
        LOGGER.info("Adding deployment for - {}", ednaJob.getMetadata().getName());

        // Get the name, and the crd spec from the factory.
        //
        String name = getUniqueDeploymentName(ednaJob);
        CustomResourceDefinition crd = ednaJobFactory.getCustomResourceDefinition();

        // TODO set up the ednajob here (by replicating the generate_job script)

        // Basically, currentResource contains all information you might need to build the docker image, push it,
        // and then create the deployment...

        // Note, we also need to make sure --> we have a label for this deployment...

        // Add the deployment with the following line:
        // client.apps().deployments().inNamespace(currentResource.getMetadata().getNamespace()).create(deployment)




        Deployment deployment = new DeploymentBuilder()
            .withNewMetadata()
                .withName(ednaJob.getMetadata().getName())
                .addToLabels(EJ_APP_LABEL_KEY, EJ_APP_LABEL_VALUE)
                .addToLabels(EJ_NAME_KEY, ednaJob.getMetadata().getName())
            .endMetadata()
            .withNewSpec()
                .withReplicas(Integer.parseInt(crd.getMetadata().getAnnotations().get("replicas")))
                .withNewTemplate()
                    .withNewMetadata()
                        .addToLabels(EJ_APP_LABEL_KEY, EJ_APP_LABEL_VALUE)
                        .addToLabels(EJ_NAME_KEY, ednaJob.getMetadata().getName())
                    .endMetadata()
                    .withNewSpec()
                        .addNewContainer()
                            .withName(name)
                            .withImage("localhost:5000/busybox")
                            .withCommand("sleep","36000")
                        .endContainer()
                    .endSpec()
                .endTemplate()
                .withNewSelector()
                    .addToMatchLabels(EJ_APP_LABEL_KEY, EJ_APP_LABEL_VALUE)
                    .addToMatchLabels(EJ_NAME_KEY, ednaJob.getSpec().getJobname())
                .endSelector()
            .endSpec()
        .build();
        LOGGER.info("Set up deployment");
        client.apps().deployments().inNamespace(ednaJob.getSpec().getApplicationname()).create(deployment);
        LOGGER.info("Applied deployment");

        LOGGER.info("Added deployment for - {}", ednaJob.getMetadata().getName());
    }



    // Delete the deployment
    public void delete(Deployment deployment){
        this.client.apps().deployments().delete(deployment);
        LOGGER.info("Deleted deployment for - {}", deployment.getMetadata().getName());
    }


}
