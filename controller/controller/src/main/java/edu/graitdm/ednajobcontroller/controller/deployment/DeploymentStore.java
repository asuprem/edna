package edu.graitdm.ednajobcontroller.controller.deployment;

import edu.graitdm.ednajobcontroller.controller.ednajob.EdnaJob;
import io.fabric8.kubernetes.api.model.apps.Deployment;

import java.util.List;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

import static edu.graitdm.ednajobcontroller.controller.ICustomResourceCommons.EJ_APP_LABEL_KEY;
import static edu.graitdm.ednajobcontroller.controller.ICustomResourceCommons.EJ_NAME_KEY;

// This keeps track of the deployments managed by the DeploymenetController.
public class DeploymentStore extends ConcurrentHashMap<Object, Deployment> {

    // Given an EdnaJob custom resource, we fetch the deployment associated with that EdnaJob
    // TODO Make sure in DeploymentFactory.add(), we add a
    //  label with key-value pair <EJ_NAME_KEY, ednaJob.getMetadata().getName()> to
    //  the generated deployment, otherwise this will not work.
    public List<Deployment> getDeploymentsforEdnaJob(EdnaJob ednaJob){
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
}
