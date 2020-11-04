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



public class NamespaceFactory {
    private static final Logger LOGGER = LoggerFactory.getLogger(NamespaceFactory.class);

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
        LOGGER.info("Set up namespace");
        client.namespaces().create(namespace);
    }


    // Delete the deployment
    public void delete(Namespace namespace){
        client.namespaces().delete(namespace);
        LOGGER.info("Deleted namespace for - {}", namespace.getMetadata().getName());
    }

    // Delete the ednajob's namespace
    public void deleteIfEmpty(EdnaJob ednaJob){
        if (deploymentStore.getDeploymentsInNamespace(ednaJob).size() == 0){
            if(namespaceStore.namespaceExists(ednaJob)){
                LOGGER.info("Deleted namespace - {}", ednaJob.getSpec().getApplicationname());
                delete(namespaceStore.getNamespace(ednaJob.getSpec().getApplicationname()));
            }
        }
    }


}
