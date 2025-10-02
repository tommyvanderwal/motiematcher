// Sample moties (motions) with historical party voting data
// Data based on Dutch Tweede Kamer voting patterns
const moties = [
    {
        id: 1,
        title: "Motie over verhoging minimumloon",
        description: "Een motie om het minimumloon sneller te verhogen dan de huidige planning voorziet.",
        votes: {
            "VVD": "tegen",
            "PVV": "neutraal",
            "CDA": "tegen",
            "D66": "voor",
            "GroenLinks": "voor",
            "SP": "voor",
            "PvdA": "voor",
            "ChristenUnie": "neutraal",
            "PvdD": "voor",
            "50PLUS": "voor",
            "SGP": "tegen",
            "DENK": "voor",
            "FvD": "tegen",
            "BIJ1": "voor",
            "Volt": "voor"
        }
    },
    {
        id: 2,
        title: "Motie klimaatdoelen 2030",
        description: "Een motie om strengere klimaatdoelen vast te stellen voor 2030, met extra investeringen in duurzame energie.",
        votes: {
            "VVD": "tegen",
            "PVV": "tegen",
            "CDA": "neutraal",
            "D66": "voor",
            "GroenLinks": "voor",
            "SP": "voor",
            "PvdA": "voor",
            "ChristenUnie": "voor",
            "PvdD": "voor",
            "50PLUS": "neutraal",
            "SGP": "tegen",
            "DENK": "voor",
            "FvD": "tegen",
            "BIJ1": "voor",
            "Volt": "voor"
        }
    },
    {
        id: 3,
        title: "Motie zorgpersoneel salarissen",
        description: "Een motie om de salarissen van zorgpersoneel structureel te verhogen en arbeidsvoorwaarden te verbeteren.",
        votes: {
            "VVD": "neutraal",
            "PVV": "voor",
            "CDA": "voor",
            "D66": "voor",
            "GroenLinks": "voor",
            "SP": "voor",
            "PvdA": "voor",
            "ChristenUnie": "voor",
            "PvdD": "voor",
            "50PLUS": "voor",
            "SGP": "voor",
            "DENK": "voor",
            "FvD": "neutraal",
            "BIJ1": "voor",
            "Volt": "voor"
        }
    },
    {
        id: 4,
        title: "Motie strengere immigratieregels",
        description: "Een motie om de regels voor immigratie en asiel aanmerkelijk te verscherpen.",
        votes: {
            "VVD": "voor",
            "PVV": "voor",
            "CDA": "neutraal",
            "D66": "tegen",
            "GroenLinks": "tegen",
            "SP": "tegen",
            "PvdA": "tegen",
            "ChristenUnie": "neutraal",
            "PvdD": "tegen",
            "50PLUS": "neutraal",
            "SGP": "voor",
            "DENK": "tegen",
            "FvD": "voor",
            "BIJ1": "tegen",
            "Volt": "tegen"
        }
    },
    {
        id: 5,
        title: "Motie belasting op vermogen",
        description: "Een motie om een extra belasting in te voeren op grote vermogens boven 1 miljoen euro.",
        votes: {
            "VVD": "tegen",
            "PVV": "neutraal",
            "CDA": "tegen",
            "D66": "neutraal",
            "GroenLinks": "voor",
            "SP": "voor",
            "PvdA": "voor",
            "ChristenUnie": "tegen",
            "PvdD": "voor",
            "50PLUS": "voor",
            "SGP": "tegen",
            "DENK": "voor",
            "FvD": "tegen",
            "BIJ1": "voor",
            "Volt": "voor"
        }
    },
    {
        id: 6,
        title: "Motie uitbreiding kernenergie",
        description: "Een motie om te investeren in de bouw van nieuwe kerncentrales als onderdeel van de energietransitie.",
        votes: {
            "VVD": "voor",
            "PVV": "voor",
            "CDA": "voor",
            "D66": "voor",
            "GroenLinks": "tegen",
            "SP": "tegen",
            "PvdA": "neutraal",
            "ChristenUnie": "neutraal",
            "PvdD": "tegen",
            "50PLUS": "neutraal",
            "SGP": "voor",
            "DENK": "tegen",
            "FvD": "voor",
            "BIJ1": "tegen",
            "Volt": "voor"
        }
    },
    {
        id: 7,
        title: "Motie woningbouw versnelling",
        description: "Een motie om de procedures voor woningbouw te vereenvoudigen en de bouw van 100.000 extra woningen per jaar mogelijk te maken.",
        votes: {
            "VVD": "voor",
            "PVV": "voor",
            "CDA": "voor",
            "D66": "voor",
            "GroenLinks": "neutraal",
            "SP": "voor",
            "PvdA": "voor",
            "ChristenUnie": "voor",
            "PvdD": "tegen",
            "50PLUS": "voor",
            "SGP": "voor",
            "DENK": "voor",
            "FvD": "voor",
            "BIJ1": "neutraal",
            "Volt": "voor"
        }
    },
    {
        id: 8,
        title: "Motie verbod op biomassa",
        description: "Een motie om het gebruik van biomassa voor energieopwekking te verbieden vanwege milieu- en natuurschade.",
        votes: {
            "VVD": "tegen",
            "PVV": "tegen",
            "CDA": "tegen",
            "D66": "neutraal",
            "GroenLinks": "voor",
            "SP": "voor",
            "PvdA": "neutraal",
            "ChristenUnie": "tegen",
            "PvdD": "voor",
            "50PLUS": "neutraal",
            "SGP": "tegen",
            "DENK": "neutraal",
            "FvD": "tegen",
            "BIJ1": "voor",
            "Volt": "voor"
        }
    },
    {
        id: 9,
        title: "Motie onderwijs investering",
        description: "Een motie om 2 miljard euro extra te investeren in het onderwijs, met name voor kleinere klassen en hogere leraarssalarissen.",
        votes: {
            "VVD": "neutraal",
            "PVV": "voor",
            "CDA": "voor",
            "D66": "voor",
            "GroenLinks": "voor",
            "SP": "voor",
            "PvdA": "voor",
            "ChristenUnie": "voor",
            "PvdD": "voor",
            "50PLUS": "voor",
            "SGP": "voor",
            "DENK": "voor",
            "FvD": "neutraal",
            "BIJ1": "voor",
            "Volt": "voor"
        }
    },
    {
        id: 10,
        title: "Motie maximumsnelheid snelwegen",
        description: "Een motie om de maximumsnelheid op snelwegen permanent te verlagen naar 100 km/u voor luchtkwaliteit.",
        votes: {
            "VVD": "tegen",
            "PVV": "tegen",
            "CDA": "tegen",
            "D66": "neutraal",
            "GroenLinks": "voor",
            "SP": "neutraal",
            "PvdA": "voor",
            "ChristenUnie": "tegen",
            "PvdD": "voor",
            "50PLUS": "tegen",
            "SGP": "tegen",
            "DENK": "neutraal",
            "FvD": "tegen",
            "BIJ1": "voor",
            "Volt": "voor"
        }
    }
];
