CONTAINER Osubdividegrid {
    INCLUDE Obase;
    NAME Osubdividegrid;
    GROUP ID_OBJECTPROPERTIES {
        REAL SG_COMPLETE {MIN 0.0; MAX 100.0; UNIT PERCENT; DEFAULT 100.0;}
        REAL SG_HOR {UNIT TIME; DEFAULT 0.0;}
        REAL SG_VERT {UNIT TIME; DEFAULT 0.0;}
    }
}
