package edu.graitdm.ednajobcontroller.controller.ednajob;

import io.fabric8.kubernetes.client.CustomResource;
import lombok.Getter;
import lombok.Setter;

// Wrapper class for the EdnaJob Custom Resource.
public class EdnaJob extends CustomResource {
    @Getter @Setter private EdnaJobSpec spec;
}
