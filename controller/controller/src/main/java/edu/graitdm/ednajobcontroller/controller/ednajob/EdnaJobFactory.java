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
    private static final Logger LOGGER = LoggerFactory.getLogger(EdnaJobFactory.class.getSimpleName());

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
            LOGGER.debug("Patching EdnaJob {} with updated state", ednaJob.getMetadata().getName());
            client.customResources(crd, EdnaJob.class, EdnaJobList.class, EdnaJobDoneable.class)
                        .inNamespace(ednaJob.getMetadata().getNamespace())
                        .withName(ednaJob.getMetadata().getName())
                        .patch(target);
        });

    }


}