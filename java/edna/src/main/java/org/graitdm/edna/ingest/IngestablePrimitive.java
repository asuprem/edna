package org.graitdm.edna.ingest;

import org.graitdm.edna.types.enums.EIngestPattern;

import java.io.Serializable;
import java.util.Iterator;
import java.util.Spliterator;
import java.util.function.Consumer;


public interface IngestablePrimitive<T extends Serializable> extends Iterable<T>{
    /** IngestablPrimitive is the base interface for an Ingest. Ingest is an iterable
     * that should run as an infinite for-loop (TODO add ways to exit out of loop)
     * Each call to the iterable returns a Serializable that is passed to the next buffer,
     * primitive, or process in the chain. The iterable should poll the message source
     * in the background, intelligently pre-fetching future stream messages.
     */

}
