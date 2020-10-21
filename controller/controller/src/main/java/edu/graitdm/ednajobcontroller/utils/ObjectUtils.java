package org.graitdm.controller.utils;

import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.util.Optional;


public class ObjectUtils {
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
