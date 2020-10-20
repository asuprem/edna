package edu.graitdm.ednajobcontroller.events;

import io.fabric8.kubernetes.api.model.HasMetadata;
import org.microbean.kubernetes.controller.AbstractEvent;
import org.microbean.kubernetes.controller.ResourceTrackingEventQueueConsumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public abstract class GenericEventQueueConsumer<T extends HasMetadata>
        extends ResourceTrackingEventQueueConsumer<T>
        implements IEventConsumerDelegate<T> {

    // Set up the logger
    private static final Logger LOGGER = LoggerFactory.getLogger(GenericEventQueueConsumer.class);

    // Create the generic listeners -- probably not to be used???
    private final List<IEventConsumerDelegate<HasMetadata>> genericListeners;
    private final List<IEventConsumerDelegate<T>> listeners;
    private final String className;

    // Constructor
    public GenericEventQueueConsumer(Map<Object, T> knownObjects) {
        super(knownObjects);
        this.genericListeners = new ArrayList<>();
        this.listeners = new ArrayList<>();
        this.className = this.getClass().getSimpleName();
    }

    @Override
    protected void accept(AbstractEvent<? extends T> event) {
        var cur = event.getResource();
        switch (event.getType()) {
            case ADDITION:
                LOGGER.trace("ADD {} {}", className, cur.getMetadata().getName());
                genericListeners.forEach(l -> l.onAddition(event));
                listeners.forEach(l -> l.onAddition(event));
                this.onAddition(event);
                break;
            case MODIFICATION:
                LOGGER.trace("MOD {} {}", className, cur.getMetadata().getName());
                genericListeners.forEach(l -> l.onModification(event));
                listeners.forEach(l -> l.onModification(event));
                this.onModification(event);
                break;
            case DELETION:
                LOGGER.trace("DEL {} {}", className, cur.getMetadata().getName());
                genericListeners.forEach(l -> l.onDeletion(event));
                listeners.forEach(l -> l.onDeletion(event));
                this.onDeletion(event);
                break;
        }
    }

    public void addGenericListener(IEventConsumerDelegate<HasMetadata> listener) {
        if (genericListeners.contains(listener)) {
            return;
        }
        genericListeners.add(listener);
    }

    public void addListener(IEventConsumerDelegate<T> listener) {
        if (listeners.contains(listener)) {
            return;
        }
        listeners.add(listener);
    }

}
