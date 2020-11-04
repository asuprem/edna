package edu.graitdm.ednajobcontroller.controller.namespace;

import edu.graitdm.ednajobcontroller.controller.ednajob.EdnaJob;
import io.fabric8.kubernetes.api.model.Namespace;

import java.util.List;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

import static edu.graitdm.ednajobcontroller.controller.ICustomResourceCommons.EJ_NAME_KEY;



// This keeps track of the deployments managed by the NamespaceController.
public class NamespaceStore extends ConcurrentHashMap<Object, Namespace> {

    // Given an EdnaJob custom resource, we fetch the deployment associated with that EdnaJob
    // TODO Make sure in DeploymentFactory.add(), we add a
    //  label with key-value pair <EJ_NAME_KEY, ednaJob.getMetadata().getName()> to
    //  the generated deployment, otherwise this will not work.
    // Returns true if namespace exists
    public boolean namespaceExists(EdnaJob ednaJob){
        return !namespaceIsUnique(ednaJob.getSpec().getApplicationname());
    }

    // Returns true if namespace name is unique (i.e. namespace does not exist)
    public boolean namespaceIsUnique(String name){
        return values().stream().noneMatch(e->e.getMetadata().getName()
                .equals(name));
    }

    public Namespace getNamespace(String name){
        return values().stream().filter(e -> e.getMetadata().getName()
                .equals(name)).collect(Collectors.toList()).get(0);
    }

    public List<Namespace> getNamespaces(String name){
        return values().stream().filter(e -> e.getMetadata().getName()
                .equals(name)).collect(Collectors.toList());
    }

}
