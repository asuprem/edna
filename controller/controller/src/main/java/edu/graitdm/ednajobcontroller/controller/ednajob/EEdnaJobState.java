package edu.graitdm.ednajobcontroller.controller.ednajob;


// All states for the EdnaJobController
// TODO (Abhijit) update with better states???
// TODO you can also update with states as and when needed, but maybe do it a little later,
//  since I am setting up the backend FSM still
public enum EEdnaJobState {
    UNDEFINED,
    DEPLOYMENT_CREATION,
    DEPLOYMENT_DELETION,
    READY
}
