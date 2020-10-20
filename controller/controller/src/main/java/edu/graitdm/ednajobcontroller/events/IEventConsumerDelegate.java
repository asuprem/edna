package edu.graitdm.ednajobcontroller.events;

import io.fabric8.kubernetes.api.model.HasMetadata;
import org.microbean.kubernetes.controller.AbstractEvent;

public interface IEventConsumerDelegate<T extends HasMetadata> {

    void onAddition(AbstractEvent<? extends T> event);

    void onModification(AbstractEvent<? extends T> event);

    void onDeletion(AbstractEvent<? extends T> event);

}
