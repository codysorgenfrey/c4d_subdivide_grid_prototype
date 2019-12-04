CONTAINER Tstainedglassgriddriver {
    NAME Tstainedglassgriddriver;
    INCLUDE Texpression;
    GROUP ID_TAGPROPERTIES {
        REAL SGGD_COMPLETE {MIN 0.0; MAX 100.0; UNIT PERCENT; DEFAULT 100.0;}
        REAL SGGD_OFF {UNIT TIME; DEFAULT -12.0;}
        REAL SGGD_OFF_MULT {DEFAULT 1.0;}
    }
}
