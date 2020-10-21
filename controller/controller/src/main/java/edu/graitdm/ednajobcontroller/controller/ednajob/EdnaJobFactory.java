package edu.graitdm.ednajobcontroller.controller.ednajob;

import io.fabric8.kubernetes.api.model.apiextensions.CustomResourceDefinition;
import io.fabric8.kubernetes.client.KubernetesClient;
import io.fabric8.kubernetes.internal.KubernetesDeserializer;
import edu.graitdm.ednajobcontroller.utils.ObjectUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import static edu.graitdm.ednajobcontroller.controller.ICustomResourceCommons.*;

public class EdnaJobFactory {
    // The logger
    private static final Logger LOGGER = LoggerFactory.getLogger(EdnaJobFactory.class);

    // The client and CRD
    private final KubernetesClient client;
    private final CustomResourceDefinition crd;

    public EdnaJobFactory(KubernetesClient client){
        this.client = client;
        /*
         * Register the CRD (see: fabric8io/kubernetes-client#1099)
         */
        KubernetesDeserializer.registerCustomKind(EJ_API_VERSION, EJ_KIND_NAME, EdnaJob.class);
        this.crd = client.customResourceDefinitions()
                    .list()
                    .getItems()
                    .stream()
                    .filter(customResources -> customResources.getMetadata()
                                .getName()
                                .equals(EJ_FULL_CRD_NAME))
                    .findFirst()                            // Take the first (because there should only be 1)
                    .orElseThrow(RuntimeException::new);    // If we don't find it. So it needs to be applied first.
    }
    public CustomResourceDefinition getCustomResourceDefinition(){
        return crd;
    }


    // This is to update the state
    public void update(EdnaJob ednaJob, EEdnaJobState state){

        ObjectUtils.deepCopy(ednaJob, EdnaJob.class).ifPresent(target -> {
            //set up to trigger onModification for the EdnaJob by updating the state in the
            // custom resource that is already in memory
            target.getSpec().setState(state);
            //Patch the custom resource in memory with the updated one with new state
            LOGGER.info("UPD - {} -- patching EdnaJob with updated state", ednaJob.getMetadata().getName());
            client.customResources(crd, EdnaJob.class, EdnaJobList.class, EdnaJobDoneable.class)
                        .inNamespace(ednaJob.getMetadata().getNamespace())  // TODO namespaces() -- we want different ones for each?? NO see below
                        .withName(ednaJob.getMetadata().getName())
                        .patch(target);
        });

    }


}
// TODO Namespace note:
//  The custom resources exist in the default namespace
//  But the applied deployments exist on their application namespace
//  So in DeploymentFactory.add(), make sure the generated deployment exists in a namespace matching the ednaJob's applicationname spec field
//  We would also need to make sure the namespace exists (Abhijit) --> for now, manually create namespace before applying ednajob
//  Also need to make sure the namespace is deleted at the end (Abhijit)