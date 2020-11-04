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

    // TODO update getters and setters here if spec is updated
    @Getter @Setter private EEdnaJobState state;
    @Getter @Setter private String import_key;
    @Getter @Setter private String export_key;
    @Getter @Setter private String jobname; // Use this to create the name for the deployment. See todo below
    @Getter @Setter private String applicationname; // Use this to apply deployment in correct namespace. See todo below
    @Getter @Setter private String filename;    // Use this to compile and apply docker. See todo below
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

    // TODO if the crd is update, update the spec here
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

/* TODO below:
     Use jobname to create the name for the deployment. This also means for the custom resource,
        this must match the metadata name. This also means there needs to be a check that the jobname field and
        the metadata.name field are the same, otherwise throw an escapable error (or warning)
     Use applicationname to apply the generated deployment to the correct namespace
     Use filename to compile docker. Make the assumption that the file exists at /some/hardcoded/path/applicationname/jobname/<filename>.py
        This also means we need to determine what the /some/hardcoded/path is, such as the user's home directory, or maybe the current directory? idk. whichever is easier.
        I think current_directoty/ednacrds/ might be a good idea? Up to you.
     Use jobcontext to get the edna context file. Basically, you need to generate the ednacontext file (ednaconf.yaml)
        The generated file should be saved to /some/hardcoded/path/applicationname/jobname/<jobcontext>.yaml
        FOR NOW THOUGH -- use a local ednaconf yaml, and don't bother generating it. We can do that in a couple weeks.
        So you could also ignore jobvariablenames and jobvariablevalues.
     jobtype is unused for now, but there because there are some ideas for it in the back of my head. You don't need to worry about it (for now, and most likely ever)
     jobimagetag, registryhost, registryport -- use these to generate the docker image programatically
        FOR THE FIRST WEEKS, generate docker tag manually and work on getting the deployment working. Then we could do docker generation.



 */