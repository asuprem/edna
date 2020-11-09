package edu.graitdm.ednajobcontroller.controller.ednajob;

import io.fabric8.kubernetes.client.CustomResourceList;

/**
 * Wrapper around kubernetes {@link CustomResourceList} for an Edna Job.
 */
public class EdnaJobList extends CustomResourceList<EdnaJob> {
}
