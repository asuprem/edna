package edu.graitdm.ednajobcontroller.events;

import io.fabric8.kubernetes.api.model.HasMetadata;
import org.microbean.kubernetes.controller.AbstractEvent;

/**
 *
 * @param <T>
 */
public interface IEventConsumerDelegate<T extends HasMetadata> {
    /**
     * The onAddition method triggers when a resource matching T is added to Kubernetes.
     * @param event Wraps around the resource that has been added. event.getCurrentResource() gets the specific
     *              resource that's added.
     */
    void onAddition(AbstractEvent<? extends T> event);

    /**
     * The onModification method triggers when a resource matching T is modified in Kubernetes.
     * @param event Wraps around the resource that has been modified. event.getCurrentResource() gets the specific
     *              resource that's modified. event.getPriorResource() gets the resource before it was
     *              modified.
     */
    void onModification(AbstractEvent<? extends T> event);

    /**
     * The onDeletion method triggers when a resource matching T is deleted in Kubernetes.
     * @param event Wraps around the resource that has been deleted. event.getCurrentResource() gets the specific
     *              resource that's deleted.
     */
    void onDeletion(AbstractEvent<? extends T> event);

}
