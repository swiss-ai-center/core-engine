import { Grid, IconButton, Link, Tooltip, Typography } from '@mui/material';
import React from 'react';
import { AllInclusiveTwoTone, DescriptionTwoTone, GitHub, PublicTwoTone } from '@mui/icons-material';
import { isSmartphone } from '../../utils/functions';

const chooseJustify = (isMobile: boolean): string => {
    return isMobile ? "center" : "space-between";
}

function Copyright() {
    return (
        <Grid container justifyContent={() => chooseJustify(isSmartphone())} alignContent={"center"}
              my={isSmartphone() ? 4 : 0}>
            <Grid item alignItems={"center"} justifyContent={"left"} display={"flex"}>
                <Tooltip title={"Website"}>
                    <Link color={"inherit"} href={"https://swiss-ai-center.ch"}
                          underline={"none"} target={"_blank"}>
                        <IconButton sx={{marginLeft: "auto"}} color={"primary"} size={"large"}>
                            <PublicTwoTone/>
                        </IconButton>
                    </Link>
                </Tooltip>
                <Tooltip title={"Documentation"}>
                    <Link color={"inherit"} href={"https://swiss-ai-center.github.io/core-engine/"}
                          underline={"none"} target={"_blank"}>
                        <IconButton sx={{marginLeft: "auto"}} color={"primary"} size={"large"}>
                            <DescriptionTwoTone/>
                        </IconButton>
                    </Link>
                </Tooltip>
                <Tooltip title={"GitHub"}>
                    <Link color={"inherit"} href={"https://github.com/swiss-ai-center/core-engine/"}
                          underline={"none"} target={"_blank"}>
                        <IconButton sx={{marginLeft: "auto"}} color={"primary"} size={"large"}>
                            <GitHub/>
                        </IconButton>
                    </Link>
                </Tooltip>
                <Tooltip title={"A guide to MLOps"}>
                    <Link color={"inherit"} href={"https://mlops.swiss-ai-center.ch"}
                          underline={"none"} target={"_blank"}>
                        <IconButton sx={{marginLeft: "auto"}} color={"primary"} size={"large"}>
                            <AllInclusiveTwoTone/>
                        </IconButton>
                    </Link>
                </Tooltip>
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
