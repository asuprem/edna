package edu.graitdm.ednajobcontroller.controller.ednajob;

import io.fabric8.kubernetes.api.builder.Function;
import io.fabric8.kubernetes.client.CustomResourceDoneable;



/**
 * Wrapper around kubernetes {@link CustomResourceDoneable} for an Edna Job.
 *
 * @see <a href="https://groups.google.com/g/fabric8/c/Q5_aSYyaAtA">Google groups discussion on
 * {@link CustomResourceDoneable}</a>
 */
public class EdnaJobDoneable extends CustomResourceDoneable<EdnaJob> {
    public EdnaJobDoneable(EdnaJob resource, Function<EdnaJob, EdnaJob> function){
        super(resource, function);
    }
}
