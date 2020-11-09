package edu.graitdm.ednajobcontroller.controller.ednajob;


import com.fasterxml.jackson.databind.annotation.JsonDeserialize;
import io.fabric8.kubernetes.api.model.KubernetesResource;

import lombok.Getter;
import lombok.Setter;

import java.util.ArrayList;
import java.util.List;

// Contains the actual specifications for the EdnaJob custom resource
@JsonDeserialize
public class EdnaJobSpec implements KubernetesResource {

    @Getter @Setter private EEdnaJobState state;
    @Getter @Setter private String import_key;
    @Getter @Setter private String export_key;
    @Getter @Setter private String jobname; // Use this to create the name for the deployment.
    @Getter @Setter private String applicationname; // Use this to apply deployment in correct namespace.
    @Getter @Setter private String filename;    // Use this to compile and apply docker.
    @Getter @Setter private String jobcontext;  // Use this to get the edna context file
    @Getter @Setter private String jobtype;     // I don't think this is important right now
    @Getter @Setter private String jobimagetag; // Setting the tag in docker
    @Getter @Setter private String jobimage; // Setting the tag in docker
    @Getter @Setter private String registryhost;// Docker registry host
    @Getter @Setter private String registryport;//Docker registry port
    @Getter @Setter private String jobdependencies;//Docker registry port
    @Getter @Setter private String filedependencies;//Docker registry port
    @Getter @Setter private List<String> jobvariablenames;  // Job variables. We can use this to create the ednaconf. See todo below.
    @Getter @Setter private List<String> jobvariablevalues;


    public EdnaJobSpec(){
        this.state = EEdnaJobState.UNDEFINED;


    }

    // This sets an EdnaJobSpecification using an existing one
    public EdnaJobSpec(EdnaJobSpec spec){

        this.state = spec.state;
        this.import_key = spec.import_key;
        this.export_key = spec.export_key;
        this.jobname = spec.jobname;
        this.applicationname = spec.applicationname;
        this.filename = spec.filename;
        this.jobcontext = spec.jobcontext;
        this.jobtype = spec.jobtype;
        this.jobimagetag = spec.jobimagetag;
        this.jobimage = spec.jobimage;
        this.registryhost = spec.registryhost;
        this.registryport = spec.registryport;
        this.filedependencies = spec.filedependencies;
        this.jobdependencies = spec.jobdependencies;

        // TODO (Abhijit) need to make sure names and values have same length
        this.jobvariablenames = new ArrayList<>(spec.jobvariablenames);
        this.jobvariablevalues = new ArrayList<>(spec.jobvariablevalues);

    }
}