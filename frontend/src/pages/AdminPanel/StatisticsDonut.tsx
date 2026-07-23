import { Box, Stack, Typography } from '@mui/material';
import React from 'react';

export type CountItem = {
    label: string;
    count: number;
    color: string;
};

export const formatStatisticLabel = (value: string) => value
    .replaceAll('_', ' ')
    .replace(/\b\w/g, (character) => character.toUpperCase());

type StatisticsDonutProps = {
    items: CountItem[];
    total: number;
    ariaLabel: string;
};

const StatisticsDonut: React.FC<StatisticsDonutProps> = ({
    items,
    total,
    ariaLabel,
}) => {
    let currentPercentage = 0;
    const segments = items.map((item) => {
        const start = currentPercentage;
        currentPercentage += total > 0 ? (item.count / total) * 100 : 0;
        return `${item.color} ${start}% ${currentPercentage}%`;
    });
    const background = total > 0
        ? `conic-gradient(${segments.join(', ')})`
        : 'conic-gradient(currentColor 0% 100%)';

    return (
        <Box
            sx={{
                display: 'grid',
                gridTemplateColumns: {xs: '1fr', sm: '220px minmax(0, 1fr)'},
                gap: {xs: 3, sm: 5},
                alignItems: 'center',
            }}
        >
            <Box
                role="img"
                aria-label={ariaLabel}
                sx={{
                    position: 'relative',
                    width: 220,
                    maxWidth: '70vw',
                    aspectRatio: '1',
                    mx: {xs: 'auto', sm: 0},
                    color: 'action.hover',
                    background,
                    borderRadius: '50%',
                }}
            >
                <Stack
                    alignItems="center"
                    justifyContent="center"
                    sx={{
                        position: 'absolute',
                        inset: '19%',
                        borderRadius: '50%',
                        bgcolor: 'background.paper',
                        color: 'text.primary',
                    }}
                >
                    <Typography variant="h4" fontWeight={650}>
                        {total.toLocaleString()}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                        Total tasks
                    </Typography>
                </Stack>
            </Box>

            <Box
                sx={{
                    display: 'grid',
                    gridTemplateColumns: '1fr',
                    rowGap: 1.75,
                }}
            >
                {items.map((item) => (
                    <Stack
                        key={item.label}
                        direction="row"
                        alignItems="center"
                        spacing={2}
                    >
                        <Stack direction="row" alignItems="center" spacing={1.25} minWidth={0}>
                            <Box
                                aria-hidden
                                sx={{
                                    width: 10,
                                    height: 10,
                                    flexShrink: 0,
                                    borderRadius: '50%',
                                    bgcolor: item.color,
                                }}
                            />
                            <Typography variant="body2" noWrap>{item.label}</Typography>
                        </Stack>
                        <Typography variant="body2" fontWeight={650} whiteSpace="nowrap">
                            {item.count.toLocaleString()}
                            <Typography
                                component="span"
                                variant="caption"
                                color="text.secondary"
                                sx={{ml: 0.75}}
                            >
                                ({total > 0 ? Math.round((item.count / total) * 100) : 0}%)
                            </Typography>
                        </Typography>
                    </Stack>
                ))}
            </Box>
        </Box>
    );
};

export default StatisticsDonut;
