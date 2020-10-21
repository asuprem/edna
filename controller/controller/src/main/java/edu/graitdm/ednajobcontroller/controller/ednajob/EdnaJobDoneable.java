package edu.graitdm.ednajobcontroller.controller.ednajob;

import io.fabric8.kubernetes.api.builder.Function;
import io.fabric8.kubernetes.client.CustomResourceDoneable;

// https://groups.google.com/g/fabric8/c/Q5_aSYyaAtA
// Basically, this is a builder class that performs the function provided (I think), and returns done() when done.
public class EdnaJobDoneable extends CustomResourceDoneable<EdnaJob> {
    public EdnaJobDoneable(EdnaJob resource, Function<EdnaJob, EdnaJob> function){
        super(resource, function);
    }
}
