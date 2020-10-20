package edu.graitdm.ednajobcontroller.controller;

import io.fabric8.kubernetes.client.KubernetesClientException;
import org.slf4j.bridge.SLF4JBridgeHandler;

import java.util.Optional;
import java.util.concurrent.locks.Condition;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

import org.apache.log4j.Level;
import org.apache.log4j.LogManager;
import org.apache.log4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.bridge.SLF4JBridgeHandler;

public class Main {
    private static final Lock lock = new ReentrantLock();
    private static final Condition terminated = lock.newCondition();

    public static void main(String[] args) {
        /*
         * Register a shutdown hook. When shutdown occurs, this thread signals the terminated condition.
         */
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            lock.lock();
            terminated.signal();
            lock.unlock();
        }));

        /*
         * Send JUL log events to SLF4J.
         */
        SLF4JBridgeHandler.removeHandlersForRootLogger();
        SLF4JBridgeHandler.install();

        /*
         * Set the JUL loggers' to the minimum verbosity.
         */
        var juls = java.util.logging.LogManager.getLogManager().getLoggerNames();
        while (juls.hasMoreElements()) {
            var logger = java.util.logging.Logger.getLogger(juls.nextElement());
            logger.setLevel(java.util.logging.Level.OFF);
        }

        /*
         * Main try block.
         */
        try {
            var logLevel = Optional.ofNullable(System.getenv("LOG_LEVEL")).orElse("DEBUG");
            var loggers = LogManager.getCurrentLoggers();
            while(loggers.hasMoreElements()) {
                Logger logger = (Logger) loggers.nextElement();
                logger.setLevel(Level.toLevel(logLevel));
            }

            org.slf4j.Logger LOGGER;
            LOGGER = LoggerFactory.getLogger(Main.class);
            LOGGER.info("Entered Main");




            /*
             * Start the Job FSM and the controllers
             */
            lock.lock();
            terminated.await(); // Here, the shutdown hook will trigger this signal
            lock.unlock();


        } catch (KubernetesClientException | InterruptedException e) {
            e.printStackTrace();
        }


    }
}
