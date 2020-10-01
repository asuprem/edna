package org.graitdm.edna.ingest;

import org.graitdm.edna.types.enums.EIngestPattern;

import java.io.Serializable;
import java.util.Iterator;
import java.util.Spliterator;
import java.util.function.Consumer;

public abstract class BaseIngest<T extends Serializable> implements IngestablePrimitive<T> {
    private static final EIngestPattern executionMode = EIngestPattern.CLIENT_SIDE_STREAM;
    protected final Serializable serializer;

    public BaseIngest(T serializer){
        this.serializer = serializer;
    }
}
