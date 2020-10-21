package edu.graitdm.ednajobcontroller.controller;

public interface ICustomResourceCommons {

    // This sets up the group for the CRD, plus the version
    String EJ_CRD_GROUP = "edna.graitdm.edu";
    String EJ_CRD_VERSION = "v1";
    String EJ_CRD_PLURAL_NAME = "ednajobs";
    String EJ_KIND_NAME = "EdnaJob";
    String EJ_FULL_CRD_NAME = EJ_CRD_PLURAL_NAME + "." + EJ_CRD_GROUP;

    // This sets up the function to generate a crd-specific tag (i.e. edna.graitdm.edu/job4, edna.graitdm.edu/v1)
    static String GROUP(String name) {
        return EJ_CRD_GROUP + "/" + name;
    }

    String EJ_API_VERSION = GROUP(EJ_CRD_VERSION);

    String EJ_APP_LABEL_KEY = "app";
    String EJ_APP_LABEL_VALUE = "ednajob";
    String EJ_NAME_KEY = GROUP("ednajob");
    // TODO add any additional global labels here
}
