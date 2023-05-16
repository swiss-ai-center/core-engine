import { Grid, Link, Typography } from '@mui/material';
import React from 'react';

const isSmartphone = (): boolean => {
    return window.innerWidth < 600;
}

const chooseJustify = (isMobile: boolean): string => {
    return isMobile ? "center" : "space-between";
}

function Copyright() {
    return (
        <Grid container justifyContent={() => chooseJustify(isSmartphone())} alignContent={"center"}>
            <Grid item alignItems={"center"} justifyContent={"left"} display={"flex"}>
                <Typography variant={"body2"} color={"text.secondary"} align={"left"} sx={{pt: 1}}>
                    <Link color={"primary"} href={"https://swiss-ai-center.ch/"} target={"_blank"}
                          sx={{textDecoration: "none"}}>
                        Official Website
                    </Link>
                    {' | '}
                    <Link color={"primary"} href={"https://github.com/csia-pme/csia-pme/"} target={"_blank"}
                          sx={{textDecoration: "none"}}>
                        GitHub
                    </Link>
                </Typography>
            </Grid>
            <Grid item alignItems={"center"} justifyContent={"center"} display={"flex"}>
                <Link color={"inherit"}
                      href={"https://www.hes-so.ch/domaines-et-hautes-ecoles/ingenierie-et-architecture"}
                      underline={"none"} target={"_blank"} marginTop={1}>
                    <img src={"/hes-so_logo.png"} alt={"HES-SO"} height={"150px"}/>
                </Link>
            </Grid>
            <Grid item alignItems={"center"} justifyContent={"right"} display={"flex"}>
                <Typography variant={"body2"} color={"text.secondary"} component={"span"} sx={{pt: 1}}>
                    {'Copyright © '}
                    <Link color={"primary"}
                          href={"https://www.hes-so.ch/domaines-et-hautes-ecoles/ingenierie-et-architecture"}
                          target={"_blank"}
                          sx={{textDecoration: "none"}}
                    >
                        HES-SO
                    </Link>
                    {' 2022-' + new Date().getFullYear() + '.'}
                </Typography>
            </Grid>
        </Grid>
    );
}

export default Copyright;
