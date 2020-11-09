package edu.graitdm.ednajobcontroller.controller.namespace;

import edu.graitdm.ednajobcontroller.controller.deployment.DeploymentFactory;
import edu.graitdm.ednajobcontroller.controller.deployment.DeploymentStore;
import edu.graitdm.ednajobcontroller.controller.ednajob.EdnaJob;
import edu.graitdm.ednajobcontroller.controller.ednajob.EdnaJobFactory;

import io.fabric8.kubernetes.api.model.apiextensions.CustomResourceDefinition;
import io.fabric8.kubernetes.api.model.Namespace;
import io.fabric8.kubernetes.api.model.NamespaceBuilder;
import io.fabric8.kubernetes.api.model.apps.Deployment;
import io.fabric8.kubernetes.client.KubernetesClient;

import org.apache.commons.lang.RandomStringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.List;

import static edu.graitdm.ednajobcontroller.controller.ICustomResourceCommons.EJ_NAME_KEY;


public class NamespaceFactory {
    private static final Logger LOGGER = LoggerFactory.getLogger(NamespaceFactory.class.getSimpleName());

    private final KubernetesClient client;
    private final NamespaceStore namespaceStore;
    private final DeploymentStore deploymentStore;

    // Constructor
    public NamespaceFactory(KubernetesClient client,
                            NamespaceStore namespaceStore,
                            DeploymentStore deploymentStore){
        this.client = client;
        this.namespaceStore = namespaceStore;
        this.deploymentStore = deploymentStore;
    }

    //Basically make sure the namespace we are, well, deploying, has a unique name.
    public boolean isUnique(String name){
        return namespaceStore.namespaceIsUnique(name);
    }

    public void add(EdnaJob ednaJob){

        LOGGER.info("Adding namespace for - {}", ednaJob.getMetadata().getName());

        String name = ednaJob.getSpec().getApplicationname();
        Namespace namespace = new NamespaceBuilder()
                                        .withNewMetadata().
                                            withName(name)
                                        .endMetadata()
                                    .build();
        LOGGER.debug("Set up namespace");
        client.namespaces().create(namespace);
    }


    // Delete the deployment
    public void delete(Namespace namespace){
        client.namespaces().delete(namespace);
        LOGGER.info("Deleted namespace for - {}", namespace.getMetadata().getName());
    }

    // Delete the ednajob's namespace
    public void deleteIfEmpty(EdnaJob ednaJob){
        List<Deployment> deploymentCollection = deploymentStore.getDeploymentsInNamespace(ednaJob);
        if (deploymentCollection.size() == 0){
            if(namespaceStore.namespaceExists(ednaJob)){
                LOGGER.debug("Deleted namespace - {} since it is empty", ednaJob.getSpec().getApplicationname());
                delete(namespaceStore.getNamespace(ednaJob.getSpec().getApplicationname()));
            }
        }
        else if (deploymentCollection.size() == 1 &&
                deploymentCollection.get(0).getMetadata().getLabels().get(EJ_NAME_KEY) == ednaJob.getMetadata().getName()){
            LOGGER.debug("Deleting namespace - {} since one 1 job remains and it is to be deleted.", ednaJob.getSpec().getApplicationname());
            delete(namespaceStore.getNamespace(ednaJob.getSpec().getApplicationname()));

        }
        else{
            //TODO (Abhijit) Fix bug where deployment is deleted but not yet registered in deploymentstore, making
            // namespacestore think there are still existing deployments
            LOGGER.debug("There are still {} deployments in the {} namespace.", String.valueOf(deploymentCollection.size()), ednaJob.getSpec().getApplicationname());
        }
    }


}
