package edu.graitdm.ednajobcontroller.utils;

import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.util.Optional;


public class ObjectUtils {
    /**
     * Copies a Kubernetes resource.
     * @param original The original object
     * @param className className of the original object
     * @param <T>
     * @return
     */
    public static <T> Optional<T> deepCopy(T original, Class<T> className) {
        T result;
        ObjectMapper objectMapper = new ObjectMapper();
        try {
            result = objectMapper.readValue(objectMapper.writeValueAsString(original), className);
        } catch (IOException e) {
            result = null;
        }
        return Optional.ofNullable(result);
    }
}
