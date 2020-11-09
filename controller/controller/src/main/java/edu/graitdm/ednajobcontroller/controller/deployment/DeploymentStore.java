package edu.graitdm.ednajobcontroller.controller.deployment;

import edu.graitdm.ednajobcontroller.controller.ednajob.EdnaJob;
import io.fabric8.kubernetes.api.model.apps.Deployment;

import java.util.List;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

import static edu.graitdm.ednajobcontroller.controller.ICustomResourceCommons.EJ_NAME_KEY;

/**
 * This keeps track of the deployments managed by the {@link DeploymentController}.
 */
public class DeploymentStore extends ConcurrentHashMap<Object, Deployment> {

    /**
     * Get deployments associated with a provided {@link EdnaJob} custom resource. Deployments
     * stored in the <code>DeploymentStore</code> are filtered using the custom resource's name
     * in the metadata and the associated namespace.
     *
     * @param ednaJob A provided custom resource
     * @return A List of deployments associated with the provided {@link EdnaJob}.
     */
    public List<Deployment> getDeploymentsForEdnaJob(EdnaJob ednaJob){
        return values().stream()
                .filter(e->e.getMetadata()
                            .getNamespace()
                            .equals(ednaJob.getSpec().getApplicationname()))
                .collect(Collectors.toList())
                .stream()
                .filter(e->e.getMetadata()
                            .getLabels()
                            .getOrDefault(EJ_NAME_KEY, "")
                            .equals(ednaJob.getMetadata().getName()))
                .collect(Collectors.toList());
    }


    /**
     * Get deployments in the application namespace associated with an {@link EdnaJob} custom resource.
     *
     * @param ednaJob A provided custom resource
     * @return A List of deployments in the application namespace of the provided {@link EdnaJob}.
     */
    public List<Deployment> getDeploymentsInNamespace(EdnaJob ednaJob){
        return values().stream()
                .filter(e->e.getMetadata()
                        .getNamespace()
                        .equals(ednaJob.getSpec().getApplicationname()))
                .collect(Collectors.toList());
    }
}
