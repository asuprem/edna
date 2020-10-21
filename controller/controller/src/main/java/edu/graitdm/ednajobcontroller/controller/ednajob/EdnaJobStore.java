package edu.graitdm.ednajobcontroller.controller.ednajob;

import io.fabric8.kubernetes.api.model.apps.Deployment;

import java.util.List;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;

import static edu.graitdm.ednajobcontroller.controller.ICustomResourceCommons.EJ_NAME_KEY;

public class EdnaJobStore extends ConcurrentHashMap<Object, EdnaJob> {

    // Given an EdnaJob custom resource, we fetch the EdnaJob associated with, well, job
    public Optional<EdnaJob> getEdnaJobWithName(String name){
        return values().stream()
                .filter(ednaJobs -> ednaJobs.getMetadata()
                        .getName()
                        .equals(name))
                .findAny();
    }
}
