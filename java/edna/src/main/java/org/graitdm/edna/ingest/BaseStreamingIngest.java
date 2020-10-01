package org.graitdm.edna.ingest;

import java.io.Serializable;

public abstract class BaseStreamingIngest<T extends Serializable> extends BaseIngest<T> {
    public BaseStreamingIngest(T serializer) {
        super(serializer);
    }
}
