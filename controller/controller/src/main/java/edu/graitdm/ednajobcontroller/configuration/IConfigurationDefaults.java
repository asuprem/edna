package edu.graitdm.ednajobcontroller.configuration;

public interface IConfigurationDefaults {
    String KUBECTL_PROTOCOL = "http";
    String KUBECTL_HOST = "127.0.0.1";
    String KUBECTL_PORT = "8080";
    String EDNA_JOB_PATHS = "";
    String EDNA_NAMESPACE = "default";
    String DOCKER_HOST_UNIX = "unix:///var/run/docker.sock";
    String DOCKER_HOST_WINDOWS = "tcp://localhost:2375";
    String EDNA_SOURCE_DIR = System.getProperty("user.dir");   // TODO (Abhijit) update to pypi
    String EDNA_APP_DIR = System.getProperty("user.dir");;


}
