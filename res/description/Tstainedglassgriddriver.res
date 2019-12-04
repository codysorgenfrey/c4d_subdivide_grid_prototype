CONTAINER Tstainedglassgriddriver {
    NAME Tstainedglassgriddriver;
    INCLUDE Texpression;
    GROUP ID_TAGPROPERTIES {
        REAL SGG_COMPLETE {MIN 0.0; MAX 100.0; UNIT PERCENT; DEFAULT 100.0;}
        REAL SGG_OFF {UNIT TIME; DEFAULT 0.0;}
        REAL SGG_VERT {UNIT TIME; DEFAULT 0.0;}
    }
}
