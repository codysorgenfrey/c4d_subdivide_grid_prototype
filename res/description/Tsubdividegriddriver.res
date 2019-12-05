CONTAINER Tsubdividegriddriver {
    NAME Tsubdividegriddriver;
    INCLUDE Texpression;
    GROUP ID_TAGPROPERTIES {
        REAL SGD_COMPLETE {MIN 0.0; MAX 100.0; UNIT PERCENT; DEFAULT 100.0;}
        REAL SGD_OFF {UNIT TIME; DEFAULT -12.0;}
        REAL SGD_OFF_MULT {DEFAULT 1.0;}
    }
}
