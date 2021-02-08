package edu.graitdm.ednajobcontroller.controller.deployment;

import edu.graitdm.ednajobcontroller.controller.ednajob.EdnaJob;
import edu.graitdm.ednajobcontroller.controller.ednajob.EdnaJobFactory;


import io.fabric8.kubernetes.api.model.OwnerReference;
import io.fabric8.kubernetes.api.model.OwnerReferenceBuilder;
import io.fabric8.kubernetes.api.model.apiextensions.CustomResourceDefinition;
import io.fabric8.kubernetes.api.model.apps.Deployment;
import io.fabric8.kubernetes.api.model.apps.DeploymentBuilder;
import io.fabric8.kubernetes.client.KubernetesClient;
import org.apache.commons.lang.RandomStringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;



import static edu.graitdm.ednajobcontroller.controller.ICustomResourceCommons.EJ_APP_LABEL_KEY;
import static edu.graitdm.ednajobcontroller.controller.ICustomResourceCommons.EJ_APP_LABEL_VALUE;
import static edu.graitdm.ednajobcontroller.controller.ICustomResourceCommons.EJ_CRD_GROUP;
import static edu.graitdm.ednajobcontroller.controller.ICustomResourceCommons.EJ_CRD_VERSION;
import static edu.graitdm.ednajobcontroller.controller.ICustomResourceCommons.EJ_KIND_NAME;
import static edu.graitdm.ednajobcontroller.controller.ICustomResourceCommons.EJ_NAME_KEY;

/**
 * <code>DeploymentFactory</code> generates new deployments for a given {@link EdnaJob}. Deployments
 * are generated using parameters extracted from the <code>EdnaJob</code>. Each generated deployment
 * contains a label in its metadata and a matching match-label for its child containers to ensure
 * they fit together.
 */
public class DeploymentFactory {

    private static final Logger LOGGER = LoggerFactory.getLogger(DeploymentFactory.class.getSimpleName());

    private final KubernetesClient client;
    private final DeploymentStore deploymentStore;
    private final EdnaJobFactory ednaJobFactory;

    /**
     * Constructor for <code>DeploymentFactory</code>
     *
     * @param client A {@link KubernetesClient} instance to communicate with the kube api-server.
     * @param deploymentStore A {@link DeploymentStore} instance to store references to existing and new
     *                        kubernetes deployments.
     * @param ednaJobFactory An {@link EdnaJobFactory} instance to retrieve existing deployments attached to an application
     *                       namespace or job.
     */
    public DeploymentFactory(KubernetesClient client, DeploymentStore deploymentStore, EdnaJobFactory ednaJobFactory){

        this.client = client;
        this.deploymentStore = deploymentStore;
        this.ednaJobFactory = ednaJobFactory;
    }

    /**
     * Checks if a given <code>name</code> is unique with respect to existing deployment names from {@link #deploymentStore}
     *
     * @param name A String to check for uniqueness.
     * @return True if name is unique.
     */
    @Deprecated
    public boolean isUnique(String name){
        return deploymentStore.values().stream().noneMatch(deployment -> deployment.getMetadata().getName().equals(name));
    }

    /**
     * Creates a unique name for a deployment by adding a random String suffix.
     *
     * @param ednaJob An {@link EdnaJob} custom resource.
     * @return A unique deployment name.
     */
    private String getUniqueDeploymentName(EdnaJob ednaJob){
        String deploymentName;
        do{
            var suffix = RandomStringUtils.random(5,true,true).toLowerCase();
            deploymentName = ednaJob.getMetadata().getName() + "-" + suffix;
        } while(!isUnique(deploymentName));
        return deploymentName;
    }

    /**
     * Add a deployment corresponding to an EdnaJob from a provided {@link EdnaJob} custom resource.
     * Deployment pulls an image from a private registry using parameters from the custom resource.
     *
     * @param ednaJob An {@link EdnaJob} custom resource.
     */
    public void add(EdnaJob ednaJob){
        /*
         * Log the add
         */
        LOGGER.info("Adding deployment for - {}", ednaJob.getMetadata().getName());

        // Get the name, and the crd spec from the factory.
        //
        String name = getUniqueDeploymentName(ednaJob);
        CustomResourceDefinition crd = ednaJobFactory.getCustomResourceDefinition();

        // Construct the complate image name for the deployment.
        String fullImageName = ednaJob.getSpec().getRegistryhost() + ":" + 
                                        ednaJob.getSpec().getRegistryport() + "/" + 
                                        ednaJob.getSpec().getApplicationname() + "-" + 
                                        ednaJob.getSpec().getJobname() + ":" + 
                                        ednaJob.getSpec().getJobimagetag();

        // Build the deployment
        Deployment deployment = new DeploymentBuilder()
            .withNewMetadata()
                .withName(ednaJob.getMetadata().getName())
                .addToLabels(EJ_APP_LABEL_KEY, EJ_APP_LABEL_VALUE)
                .addToLabels(EJ_NAME_KEY, ednaJob.getMetadata().getName())
                .withOwnerReferences(new OwnerReferenceBuilder()
                        .withApiVersion(EJ_CRD_GROUP + '/' + EJ_CRD_VERSION)
                        .withKind(EJ_KIND_NAME)
                        .withName(ednaJob.getMetadata().getName())
                        .withUid(ednaJob.getMetadata().getUid())
                        .withController(true)
                        .withBlockOwnerDeletion(true).
                                build())
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
                            .withImage(fullImageName)
                        .endContainer()
                    .endSpec()
                .endTemplate()
                .withNewSelector()
                    .addToMatchLabels(EJ_APP_LABEL_KEY, EJ_APP_LABEL_VALUE)
                    .addToMatchLabels(EJ_NAME_KEY, ednaJob.getMetadata().getName()) //TODO(Abhijit) fix this with more stringent controls
                .endSelector()
            .endSpec()
        .build();
        LOGGER.debug("Set up deployment");
        client.apps().deployments().inNamespace(ednaJob.getSpec().getApplicationname()).create(deployment);
        LOGGER.info("Applied deployment for - {}", ednaJob.getMetadata().getName());

    }


    /**
     * Delete a deployment.
     * @param deployment The deployment to delete.
     */
    public void delete(Deployment deployment){
        this.client.apps().deployments().delete(deployment);
        LOGGER.info("Deleted deployment for - {}", deployment.getMetadata().getName());
    }


}
