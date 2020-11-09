package edu.graitdm.ednajobcontroller.controller.ednajob;

import io.fabric8.kubernetes.client.CustomResource;
import lombok.Getter;
import lombok.Setter;

/**
 * Wrapper around kubernetes {@link CustomResource} for an Edna Job.
 */
public class EdnaJob extends CustomResource {
    @Getter @Setter private EdnaJobSpec spec;
}
