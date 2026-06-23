| OpenSatMap: | A Fine-grained  | High-resolution |              | Satellite |
| ----------- | --------------- | --------------- | ------------ | --------- |
| Dataset     | for Large-scale | Map             | Construction |           |
HongboZhao1,3∗ LueFan1,3∗† YuntaoChen2∗ HaochenWang1,3∗ YuranYang4,5∗
| XiaojuanJin1 | YixinZhang4 | GaofengMeng1,2,3 | ZhaoxiangZhang1,2,3† |     |
| ------------ | ----------- | ---------------- | -------------------- | --- |
1InstituteofAutomation,ChineseAcademyofSciences(CASIA)
4202 tcO 03  ]VC.sc[  1v87232.0142:viXra
2CentreforArtificialIntelligenceandRobotics,HKISI,CAS
3UniversityofChineseAcademyofSciences(UCAS)
| 4TencentMaps,Tencent | 5BeijingUniversityofPostsandTelecommunications |     |     |     |
| -------------------- | ---------------------------------------------- | --- | --- | --- |
https://opensatmap.github.io
| w/o. labels |     | Cross-River Bridge | Winding Road |     |
| ----------- | --- | ------------------ | ------------ | --- |
w/. labels
Figure1:DemonstrationsofOpenSatMapdataset. Itcontainshigh-resolutionsatelliteimageswith
fine-grainedannotations,coveringdiversegeographiclocationsandpopulardrivingdatasets[8,11].
Abstract
Inthispaper,weproposeOpenSatMap,afine-grained,high-resolutionsatellite
datasetforlarge-scalemapconstruction.Mapconstructionisoneofthefoundations
| ofthetransportationindustry,suchasnavigationandautonomousdriving. |     |     |     | Extract- |
| ----------------------------------------------------------------- | --- | --- | --- | -------- |
ingroadstructuresfromsatelliteimagesisanefficientwaytoconstructlarge-scale
maps.However,existingsatellitedatasetsprovideonlycoarsesemantic-levellabels
witharelativelylowresolution(uptolevel19),impedingtheadvancementofthis
field. Incontrast,theproposedOpenSatMap(1)hasfine-grainedinstance-level
annotations;(2)consistsofhigh-resolutionimages(level20);(3)iscurrentlythe
largestoneofitskind;(4)collectsdatawithhighdiversity.Moreover,OpenSatMap
coversandalignswiththepopularnuScenesdatasetandArgoverse2datasetto
| potentiallyadvanceautonomousdrivingtechnologies. |     |     | Bypublishingandmain- |     |
| ------------------------------------------------ | --- | --- | -------------------- | --- |
tainingthedataset,weprovideahigh-qualitybenchmarkforsatellite-basedmap
constructionanddownstreamtaskslikeautonomousdriving.
∗Equalcontribution.
†Correspondingauthor.
38thConferenceonNeuralInformationProcessingSystems(NeurIPS2024)TrackonDatasetsandBenchmarks.

1 Introduction
Large-scale, up-to-date, andfine-grainedmapconstructionisfundamentaltomanytaskssuchas
trafficcontrolandautonomousdriving. Comparedwithon-roadmapping,constructingmapsfrom
satelliteimagesisahighlyefficientwayforthispurposebecauseofthelargegeographiccoverage.
Althoughitispromising,parsingfine-grainedroadstructuresfromsatelliteimagesformapconstruc-
tionisahighlychallengingtaskforthefollowingreasons. (i)Theresolutionofsatelliteimagesis
usually not high enough for fine-grained lane line detection. For example, the common level-19
satelliteimageshavearesolutionof30cmperpixel,whichcanbarelymakeoutalanelinethatis
20cmwide. (ii)Thelanelinesinmoderncitiespossesshighlycomplextopologicalstructuresand
function-basedsemantics. Itnotonlyposeschallengesfordesigningmodelswithenoughcapacities
butalsomakesitdifficulttobuildfine-graineddatasets.
Existingbenchmarks[6,14,18,30,22]havemadeattemptstohandlethechallengingtasks.However,
theyeachhavetheirlimitations,preventingthemfromeffectivelysupportinglarge-scaleandfine-
grainedmapconstruction. Specifically,existingbenchmarkshavethefollowinglimitations.
• Coarse annotations. All of these benchmarks support only coarse semantic-level lane
segmentation,whichisfarfromenoughtoparsefine-grainedlanemarkingswithvarious
functionalitiesandhighlycomplicatedtopologies.
• Lowresolution. Theimagesinexistingbenchmarksoftenhaverelativelylowresolutions.
The highest resolution they have is 0.3 m per pixel, which is inadequate for accurate
perceptionoflanelines.
• Smallscale. Existingbenchmarkshaverelativelysmallscales. Thelargestofthemhave
lessthan10k1024×1024images.
• Unalignmentwithautonomousdrivingbenchmarks. Existingbenchmarkssolelyfocus
onspecificregions,limitingtheirfurtherapplicationsinautonomousdriving,whichalso
heavilyreliesonmapconstruction.
Table1showsthebasicinformationofthem. Giventhelimitationsofexistingbenchmarksandthe
challengesofthistask,weconstructOpenSatMap,anewdatasetformapconstructionfromsatellite
images,withthefollowinguniquefeatures.
• Fine-grainedinstance-levelannotations. Unlikethecoarsesemanticlevelannotations
inpreviousdatasets,wecarefullylabelfine-grainedinstance-levellanelinesaccordingto
fine-grainedlineattributes.
• Higherresolution. Wecollectlevel-20satelliteimageswitharesolutionof0.15mper
pixel,whichishigherthantheresolutionsofallpreviousbenchmarks. Consideringthedata
accessibilityanddiversity,weadditionallyprovidelevel-19imageswitharesolutionof0.3
mperpixel.
• Largerscale. Wecollectandcarefullyannotate38k1024×1024imagesandaround445k
instances,whichisaround5xlargerthanthelargestoneofthepreviousdatasetsintermsof
thenumberofimages.
• Higherdiversity. Wecollectdatafrom60citiesand19countriesaroundtheworld. The
collecteddataishighlydiverseandcoversvariousroadtypes,geographicenvironments,
specialstructures,andtrafficregulations.
• Alignmentwithautonomousdrivingbenchmarks. Inordertoadvancethemapconstruc-
tioninautonomousdriving,OpenSatMapcoverstheregionsofnuScenes[8]andArgoverse
2[11]datasets,whicharethemostpopularautonomousdrivingdatasets. Inaddition,we
manuallyaligntheGPSlocationsofourdatawiththemforpracticaluse.
Giventhesecharacteristics,webelieveOpenSatMapcanserveasafoundationforvariousapplications,
includingcity-scalemapconstruction,lanedetection,andautonomousdriving.
2 RelatedWork
SatelliteImageryDatasets. Satelliteimagerydatasetscanbeusedforseveralcomputervisiontasks
suchasinstancesegmentation[24,46,15],objectdetection[20,50,19,33],semanticsegmentation
2

Table1: Comparisonagainstpreviousdatasets. OpenSatMapisthelargestroadextractiondataset
withthehighestresolutionandthemostdetailedannotations. ∗denotesthatwestandardizethesize
ofimagesto1024×1024andcalculatethenumberofimagesinalldatasets.
| Dataset           | #ofImages∗ | Resolution  | GTSource | LabelingLevel | Region      |
| ----------------- | ---------- | ----------- | -------- | ------------- | ----------- |
| Massachusetts[39] | 2513       | 1.00m/pixel | OSM      | Semantic      | America     |
| CasNet[14]        | 77         | 1.20m/pixel | Manually | Semantic      | -           |
| DeepGlobe[18]     | 8570       | 0.50m/pixel | QGIS     | Semantic      | 3Counties   |
| SpaceNet[47]      | 4481       | 0.31m/pixel | OSM      | Semantic      | 4Counties   |
| Roadtracer[6]     | 4800       | 0.60m/pixel | OSM      | Semantic      | 6Counties   |
| Ottawa[37]        | 235        | 0.30m/pixel | Manually | Semantic      | Canada      |
| CHN6-CUG[54]      | 4511       | 0.50m/pixel | Manually | Semantic      | China       |
|                   | 7224       | 0.30m/pixel |          | Instance,     | 60Cities,   |
| OpenSatMap(Ours)  |            |             | Manually |               |             |
|                   | 31696      | 0.15m/pixel |          | Vectorized    | 19Countries |
[49, 10, 42, 37], scene classification [43, 31], and change detection [17, 40, 45, 12] etc.. These
datasetsincludeopticalandhyper-spectralimageswithvaryingresolutions,coveringawiderange
of application fields such as urban [41, 10], agricultural [24, 15], transportation [37, 7, 6] and
marine [3, 25] areas on a global scale. They provide a wealth of labeling information, such as
buildingoutlines,roadnetworks,vegetationtypes,waterdistribution,etc.,whichgreatlypromotesthe
developmentofdeeplearninginthefieldofremotesensingimages. Inthispaper,weareinterested
intheapplicationofsatelliteimagesonroadextractionandwewilldiscussthedatasetsforroad
constructionusingremotesensingimagerylater.
SatelliteImageryDatasetsforRoadExtraction. Earlydatasetsmainlyfocusonsemanticlabeling
forthesatelliteimagesandcontributesignificantlytosemantic-levelroadextraction. Massachusetts
[39] contains 1171 images of size 1500 × 1500 with a resolution of 1 m/pixel. DeepGlobe [18]
collectsimagesfromThailand,Indonesia,andIndiaandscrapeslabelsfromQGIS[5]. Itcontains
8570imageswithimagesize1024×1024. Roadtracer[6]usesOpenStreetMap[4]tolabel300
imagesfrombigcitieswith0.6m/pixel. SpaceNet[47]contains2780imagescollectedfromLas
Vegas, Paris, Shanghai, and Khartoum. There are some datasets manually labeled. Ottawa [37]
collectsseveraltypicalurbanareaswith0.30m/pixelspatialresolutionandannotatestheroadsurface,
roadedgesandroadcenterlines. CHN6-CUG[54]collects6citiesinChinawith0.5m/pixel. and
CasNet[14]iscomposedof224imageswithaspatialresolutionof1.2mperpixel.
However, existing satellite road extraction datasets tend to be relatively small [37, 14, 29, 53],
or labeled by OpenStreetMap [47, 39, 6] and QGIS [18, 52] platforms, which are limited by the
metainformationinthedatabase. Besides,semanticlabelingresultsinawealthofunder-utilized
information. Withtheboomingdevelopmentofhigh-resolutionremotesensingimagery,academics
urgentlyneedahigherresolution,morerichlylabeleddataset. Ourworkfillsthisgapbyprovidinga
highquality,higherresolution,andbiggerdatasetwithinstance-levelvectorizedannotations. The
readersmayrefertoTable1foradetailedcomparisonagainstpreviousdatasets.
3 OpenSatMapDataset
Inthissection,weintroduceourpipelinetocollect(Sec. 3.1),annotate(Sec. 3.2)high-resolution
| satelliteimagesanddemonstratethestatisticsofOpenSatMapinSec. |     |     |     | 3.3. |     |
| ------------------------------------------------------------ | --- | --- | --- | ---- | --- |
3.1 DataCollection
WecollectimagesfromGoogleMaps[1]usingpublicMapsStaticAPI,whichispubliclyavailable
and has been processed by Google to remove sensitive information. Considering the limitations
mentionedinSec.1,wecollectthedataOpenSatMapwiththefollowingguidelinesandfactors.
Highresolution. Tofulfillthegoalofhigherresolution. Wecollectlevel-20satelliteimages,which
have a resolution of 0.15 cm/pixel. In this way, our dataset has a higher resolution than all the
existingdatasetsasTable1shows. GoogleMapsdoesnothavereallevel-20imagesinsomeregions.
Therefore, during the collection, we carefully verify the resolution for each image to avoid the
3

Front
Back Right
Back
(a)Landmarkcorrespondencesbetweenasatellite (b)OverlayingthedrivingtrajectoriesfromthenuScenes
imageandanuScenesimage. datasetontoOpenSatMap(BostonSeaport).
Figure2: Alignmentwithdrivingbenchmark.
“pseudolevel-20images”whichareactuallyresizedfromlevel-19images. Consideringthepractical
requirementsofusers,wealsoadditionallycollectlevel-19images. Tobeprecise,OpenSatMap19
standsforthelevel-19part,andOpenSatMap20standsforthelevel-20part.
GeographicDiversity Theroadsindifferentgeographiclocationsexhibitsignificantdifferencesin
thesurroundingnaturalenvironment,constructionregulations,spatialdistribution,roadconditions,
and appearance. To ensure such diversities, we sample the geographic locations considering (i)
famousandtypicalcitiesaroundtheworld; (ii)terrainwithdifferentappearancessuchasplains,
mountains,anddeserts;(iii)regionswithdifferentroaddensitiessuchasurbanandsuburban. Inthis
way,weensuretheoveralldiversityofourdatasetbycontrollingthegeographicdiversity. Inthe
following,wetakemorefactorsintoaccounttofurtherimprovethedataqualityanddiversity.
SpecialRoadStructures Unlikethecommonstraightroads,someroadshavespecialandcom-
plicatedstructuressuchasflyovers,roundabouts,andwindingroads. Thelaneinstancesofthese
regionsdemonstratedifferentshapesanddistributionsfromthestraightlanes. Toensurethemodels
trainedonourdatacouldwellhandlethesestructures,wemanuallysearchandcollectsomeregions
containingthem. Figure1showsexamplesofspecialroadstructures.
TrafficFeature Hereweusethetermtrafficfeaturetorepresentleft-hand/right-handtrafficregula-
tionsandvehicledensity. Theleft-hand/right-handregulationsdeterminethedirectionoflanes. The
vehicledensityhasanimpactonthedifficultyoflanedetectionsincevehiclesmayoccludethelanes.
Duringdatacollection,wedeliberatelyconsidertheregionswithdifferentdrivingregulationsand
balancethesampleswithdifferentvehicledensities.
Alignment with Driving Benchmark To facilitate the map construction task in the field of
autonomousdriving,wemakethecollectingregionsfullycoverthedrivingregioninfamousdriving
benchmarknuScenes[8]andArgoverse2[11]. SinceArgoverse2onlyprovidestherelativepose
withoutGPS,wemanuallyrecognizeacoupleoflandmarksofeachcityinArgoverse2andfindthe
GPScoordinatesoftheselandmarks. ThentheGPScoordinatesofallsamplesinArgoverse2canbe
derivedbytherelativeposes. Figure2showcasesthealignment.
3.2 Annotation
After the data collection, we employ experienced annotators to carefully annotate the data at a
fine-grainedinstancelevel. Theannotationsareperformedbyaprofessionalremotesensingimagery
labeling team of approximately 50 annotators for labeling and 7 for quality checking. The total
costoflabelingisroughly$72,000,i.e.,$19perimage. Notethat,forlabeling,theimagesizeof
OpenSatMap20wecollectis4096×4096and2048×2048forOpenSatMap19.
4

Guide Line
Bus Lane
Virtual Line Curb
Chevron Markings Vehicle Staging Area
Lane Line
Dash Line Solid Line Short Dash Line
(a)Anexampleofthreecategories. (b)Examplesofattributes.
Figure3: Examplesofcategoriesandattributes.
Linerepresentation. Torepresentthelanelineswithhighlyvariablelengthsandcurvatures,we
adoptvectorizedpolylinesastherepresentation. Eachlinecontainsawealthofcategoryandattribute
information. Meanwhile,theorderofthepointsinthepolylinesdefinesthelinedirection.
Linecategories. Wefirstcategorizealllinesintothreecategories: curb,laneline,andvirtualline.
Acurbistheboundaryofaroad. Lanelinesarethosevisiblelinesformingthelanes. Avirtualline
meansthatthereisnolanelineorcurbhere,butlogicallythereshouldbeaboundarytoformafull
lane. Forexample,aforkintheroadbreaksacurbintotwosegments,thenweuseavirtuallineto
connectthetwosegments. Figure3ashowsexamplesofthesethreecategories.
Whereshoulditbelabeled? Generallyspeaking,welabelallthreecategoriesabove. However,
thereisusuallyocclusioninthesatelliteimages. Ifalineispartiallyoccludedbybuildings,trees,and
vehiclesbutitscompleteshapecanbeinferredwithhighconfidence,weannotateit. Fullyoccluded
linesarenotlabeled. Aspecialcaseisthatoverpassesusuallyoccludethebottomroads,wherethe
occludedpartisnotlabeled. Weshowthesecasesinthesupplementarymaterials.
Fine-grained line attributes. Lines are as-
signedwithacoupleofattributesbasedontheir
appearance and functionalities. Specifically, AttributeChange
thereare8attributesasfollows: Fork & Merge
• Thecolorsoflines.
• The line type such as solid line, thick solid
line,dashedline,andshortdashedline.
• Thenumberoflinessuchassinglelinesand
doublelines.
• Lineswithspecialfunctionalitiessuchasbus (a)Attributechange. (b)Linesforkandmerge.
lanes,guidelines,lane-borrowingareas.
• Whetheritisbi-directional.
Figure4:Definitionofinstances(zoominforbest
• Whetheritistheoutermostboundaryofthe viewing). In(a), achangeoflinetyperesultsin
pavement. twoinstancessharingthesamepoint. In(b),aline
• Thelevelofocclusion. shouldbedividedintothreeinstanceswhenitis
• Thelevelofclearness. forkedormerged.
Figure3bshowssomeexamplesofdifferentattributes.
Instancesdefinition. Afterdefiningthelineattributes,wefurtherdefinetheinstanceusingthe
followingguidelines. (i)Differentinstanceshavedifferentattributes. Forexample,ifasolidline
becomes a dashed line, we cut the line into two instances. Figure 4a shows an example of such
attribute change. (ii) When lines fork or merge (e.g., “Y”-shape point), we break the lines into
multipleinstancesasFigure4bshows.
5

1 W 59 h , i 6 te 06 105 S , o 0 l 1 i 7 d S 1 i 7 n 3 g ,7 le 92 Chevr 2 o 3 n , 0 m 9 a 2 rkings
1
L
8
a
1
n
,
e 644 4 D 2, a 7 s 3 h 3
1
L
8
a
1
n
,
e 644
1
L
8
a
1
n
,
e 642
Functional Lane
Ye 2 ll 1 o ,7 w 26 8 C 0 N u ,5 o r 7 b n 4 e 2 V 7, i 8 rt 3 u 9 al 27 N ,8 o 3 n 9 e Thi 2 ck 7 Shor , t O D th s e9r 9 s55 a4s9h o 9 L 4 1 in l e 8 id 8 C 0 N u ,5 o r 7 b n 4 e 2 V 7, i 8 rt 3 u 9 al 27 N ,8 o 3 n 9 e Dou 7 b 8 le 30 8 C 0 N u ,5 o r 7 b n 4 e 2 V 7, i 8 rt 3 u 9 al 27 N ,8 o 3 n 9 e 14 P ,2 a 8 rk 6 ing 47,355 G 58 u 5 id 2 e N 1 o 3 P 0 a D 9 r e k c8e i 0 Bl n u e s 9 V r g e a hi t T c ida i l4l 7o e 8 9 0 n s8ta 716 ging
80,574 80,574 80,574
(a)Colordistribution. (b)Linetypedistribution. (c)#linesdistribution. (d)Functiondistribution.
1 F 6 a 3 l , s 5 e 21 9 T 0, r 8 u 4 e 9 109, N 40 o 0 1 C 7 le 8 a ,4 r 26
T 1 ru 8 e ,123 1 L 8 a 1 8 n 8 C , 0 e F 6 0 u , a 4 5 , r 5 l 4 7 b s 3 4 e 4 2 V 7, i 8 rt 3 u 9 al 27 F ,8 al 2 s 6 e 9 F 0 a ,7 ls 9 e 5 1 L 8 a 1 8 n 8 C , 0 e 6 T 0 u , 4 5 , r r 2 u 4 7 b 4 e 4 7 2 V 7, i 8 rt 3 u 9 al 21 T ,5 r 5 u 5 False3 e 27 False 6284 6 M 0 M , i 1 a 5 n j 1 o , 1 7 r o 31 3 r 5 M 1 3 L 8 , i a 1 n 1 8 n C 7 o , 0 e 6 9 r u , 4 5 r 4 7 b 4 2 1 V 7 8, , i 0 8 r 2 t 3 u 3 9 a N l o 24 93 M 7 , 2 N a 9 jor 8 o 8 M24in3o0Mr4a2j1or Fuz3zy218 1 L 8 a 1 8 n 7 C , C 0 e 6 9 u , 4 l , 5 r e 9 4 7 b a 5 4 r 8 2 V 7, i 8 rt 3 u 9 al 27 C ,8 le 3 a 6 3 F1u6zzy r
(e)Bidirectiondistribution. (f)Boundarydistribution. (g)Occlusiondistribution. (h)Clearnessdistribution.
Figure6: DistributionoflineattributesinOpenSatMap20.
Image-leveltags. Furthermore,weprovideOpenSatMap20with4additionalimage-leveltagsto
describegeneralinformation,includingimageclearness,overallvehicledensity,urban/suburban/rural,
andtheexistenceofspecialroadstructures. Wepresentthedetailsinthesupplementarymaterials.
3.3 StatisticsofOpenSatMap
In this section, we summarize the statistics of # Instance (ZOOM=19) # Instance (ZOOM=20)
the established OpenSatMap. There are 1806 100 120
80 100
2048×2048imagesinOpenSatMap19and1981
4096×4096imagesinOpenSatMap20. Weran- 60 80
60
domlydividedthemintotrainingset,validation 40
40
setandtestingsetintheratioof6:2:2. Figure5 20 20
showsthenumberofinstancesineachimagein 0 0
0 50 100150200250300350 0 100 200 300 400 500 600
OpenSatMap19andOpenSatMap20. Thenum-
Figure 5: Number of instances in each image in
ber of instances of most images is under 300.
OpenSatMap19(left)andOpenSatMap20(right).
Figure6illustratesthedistributionsofattributes.
Mostattributeshaveanon-uniformdistribution,
whichreflectstherealconditionoftheroads. Figure7showsthetagdistributioninOpenSatMap20.
4 Instance-levelLineDetection
4.1 FormulationsandBaselineMethod
Given an input image I ∈ RH×W×3, where H × W indicates the input resolution, we aim to
detecteachlineinstanceintheinputimage. Foreachinstance,weusepolylinesasthevectorized
representationandpixel-wiseinstance-levelmasksastherasterizedrepresentation. Apolylineis
definedasasetofpointsp ∈ RN×2, whereN meansthenumberofsampledpoints. p[:,0]and
p[:,1] represent the x and y coordinates, respectively. One can rasterize polylines to pixel-level
masksbysimplyconnectingadjacentpointswithlineswithapre-definedlinewidth.
The instance-level line detection task needs to convert an RGB image I into a set of polylines
{p }M ,whereM isthenumberofinstances. Wedevelopasimplebaselinewithoutwhistleand
i i=1
bellsillustratedinFigure8. Wedecomposethistaskinto3steps: (1)semanticsegmentation,(2)
instancedetection,and(3)instancevectorization.(2)and(3)arepost-processingtechniques.Detailed
formulationsforeachstepareprovidedasfollowsandimplementationdetailsareprovidedinthe
Supplementarymaterials.
6

Post-Processing
|     |              | Semantic |     | Instance  |     |               | Instance |     |     |
| --- | ------------ | -------- | --- | --------- | --- | ------------- | -------- | --- | --- |
|     | Segmentation |          |     | Detection |     | Vectorization |          |     |     |
Satellite Image Semantic Prediction Instance Prediction Denoised Instance Prediction
|          |              |      | Figure8: Illustrationofourbaselinemethod. |      |                              |      |      |                         |     |
| -------- | ------------ | ---- | ----------------------------------------- | ---- | ---------------------------- | ---- | ---- | ----------------------- | --- |
|          |              |      |                                           |      | Image ClarityVehicle Density |      | Area | Special Road Structures |     |
|          |              |      | RH×W×3                                    |      |                              |      |      | 1320                    |     |
| Semantic | segmentation |      | f :                                       | →    |                              |      |      |                         |     |
| {0,1,··· | ,C − 1}H×W   | aims | to classify                               | each | 1200                         | 1138 |      |                         |     |
1106
| pixel into | a unique | semantic | category, | where |     |     |     |     |     |
| ---------- | -------- | -------- | --------- | ----- | --- | --- | --- | --- | --- |
1000
| C is the | number | of categories. | We  | denote |     |     | 924 |     |     |
| -------- | ------ | -------------- | --- | ------ | --- | --- | --- | --- | --- |
861
800
| y=f(I)asthesegmentationresult. |     |     | Weadopt |     |     |     |     |     |     |
| ------------------------------ | --- | --- | ------- | --- | --- | --- | --- | --- | --- |
637
SegNeXt[27]asthesegmentationnetworksince
|     |     |     |     |     | 600 | 547 |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
itisquiteefficientforhigh-resolutionimages.
|     |     |     |     |     |     |     | 406 |     | 422 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
400
| Instance  | detection | g                | : {0,1}H×W | →        |      | 282  |       |            |     |
| --------- | --------- | ---------------- | ---------- | -------- | ---- | ---- | ----- | ---------- | --- |
| {0,1,···  | ,M}H×W    | converts         | the binary | seg-     | 200  |      |       | 150 174    |     |
| mentation | mask      | of each category | into       | a pixel- | 0    |      |       |            |     |
|           |           |                  |            |          | CCPC | Sp M | D S R | U B N RAOP |     |
levelmask,whereeachinstancesharesthesame
value within this mask. Technically, we first Figure7: Image-leveltagdistributioninOpen-
extract the binary mask y ∈ {0,1}H×W of SatMap20. CC=completeclear,PC=partially
c
each category c and then apply the watershed clear,Sp=sparse,M=moderate,D=dense,S=
suburban,R=rural,U=urban,B=bridge,N=
algorithm[2]toobtaininstance-levelmasks.
None,RA=roundabout,OP=overpass.
| Instance | vectorization | h   | : {0,1}H×W | →   |     |     |     |     |     |
| -------- | ------------- | --- | ---------- | --- | --- | --- | --- | --- | --- |
RN×2aimstobuildavectorizedrepresentation
ofeachinstance,whichcontains(1)instancedenoising,and(2)pointsampling. Instancedenoising
followsasimplesample-then-reconstructpipeline. Specifically,foreachinstanceithatbelongsto
categoryc, wefirstextractitsbinarymaskyi ∈ {0,1}H×W. WesubsequentlysampleN
|                             |     |     |        | c   |     |     |     |     | points |
| --------------------------- | --- | --- | ------ | --- | --- | --- | --- | --- | ------ |
| andobtaintheircoordinatespi |     |     | ∈RN×2. |     |     |     |     |     |        |
Then,wesimplyconnectadjacentpointswithlinesand
c
removeinstanceswithfewerthan100pixels,obtainingthedenoisedinstancemapyˆi =h(yi)for
c c
eachinstanceithatbelongstocategoryc. Notethatyˆi isthefinalrasterizedrepresentationofaline
c
instance. Asforpointsampling,wesampleN pointsfromyˆi,resultinginpˆi =ϕ(yˆi)tobuildthe
|     |     |     |     |     | c   |     | c   | c   |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
vectorizedrepresentation.
4.2 Evaluation
Semantic-levelevaluation. Weadoptthemeanintersectionoverunion(mIoU)[21]overdifferent
categoriesasthemetrictoevaluatetheperformanceatthesemanticlevel.
Instance-level evaluation. We adopt the average precision (AP) as the metric to evaluate the
performanceattheinstancelevel. Underinstancesegmentationsettings,acommonpracticeisto
usetheMaskAP(APM)byleveragingamaskIoUthresholdtoidentifywhetheraninstanceisa
true positive sample or not [13, 48, 36, 9, 28]. However, line markings typically exhibit narrow
featuresandsegmentationoutputsfrequentlylackprecisioninedgedefinition. Consequently,relying
exclusivelyonMaskIoUthresholdsmaybeexcessivelystrict. Tothisend,weincorporateChamfer
Chamferdistancebetweentwosetsofpointsp∈RM×2
distanceproposedby[34]asanalternative.
andq∈RK×2isdefinedas:
M
1 (cid:88)
|     |     |     | D (p,q)= |     | min | d(p ,q | ),  |     | (1) |
| --- | --- | --- | -------- | --- | --- | ------ | --- | --- | --- |
|     |     |     | Chamfer  |     |     | i j    |     |     |     |
M j=1,2,...,K
i=1
whered(·,·)istheEuclideandistancebetweentwopoints. Then, wegetChamferAP(APC)by
D
choosingthedistancethresholdD.
7

Table 2: Evaluation on OpenSatMap validation set. The line width is set to 6 pixels in Open-
SatMap20and3pixelsinOpenSatMap19bydefault. APMmeansthatthemaskIoUisusedwhen
determiningtruepositives,whileAPC meansChamferAPwithathresholdofDmeters.AP denotes
D x
thatthethresholdissettox. AP indicatestheaveragedvalues,varyingthethresholdfromxtoy.
x:y
Dataset APC APC APC APC APM APM APM mIoU
0.9 1.5 3.0 4.5 50:95 50 75
OpenSatMap19 16.04±0.35 22.68±0.35 26.88±0.52 29.18±0.22 3.66±0.15 10.66±0.44 1.45±0.12 28.71±0.38
OpenSatMap20 20.30±0.21 25.93±0.35 29.50±0.40 31.38±0.43 6.98±0.21 16.05±0.32 5.26±0.13 33.69±0.45
Figure9: QualitativeresultsonOpenSatMap19(thefirsttworows)andOpenSatMap20(thelast
tworows)testsplit. Foreachscene,weput(a)theinputimage,(b)theinstanceprediction,(c)the
denoisedinstanceprediction,and(d)theannotation,fromlefttoright,respectively.
4.3 Mainresults
EmpiricalresultsinTable2indicatethatinstance-levellinedetectionisamuchmorechallenging
taskcomparedwithsemantic-levelsegmentation,sincevaluesofAPCandAPMaremuchlowerthan
thatofmIoU.
Fundamentally,thisissuearisesbecauseinstancesareassociatedwithfine-grainedattributeswhile
semantic segmentation only involves several categories. Consequently, identifying true positive
instancepredictionsbecomesanotablydifficulttask.
Qualitativeresults. WeprovidequalitativeresultsinFigure9. Ourmethodmanagestodetectline
instances. Although the visual results of our model are almost satisfactorily presented, they are
accompaniedbydisappointinglylowquantitativescoresofAPCandAPM. Usually,ourmethodfails
todetectaccuratelineinstances,whenthesegmentationperformspoorly,suchasfailingtopredict
separatemaskswhenattributeschange,andadheredsegmentationmasksoftwoseparatelines. This
disparityindicatesthatthisbenchmarkisofsubstantialdifficulty,necessitatingdeeperexplorationof
aneffectiveend-to-endmethod.
5 PotentialApplicationinAutonomousDriving
Tofacilitatethemapconstructiontaskinautonomousdriving,wemakeOpenSatMapdeliberately
cover the regions of nuScenes [8] and Argoverse 2 [11] datasets. Recently, a line of work has
provedtheeffectivenessandsuccessofusingadditionalmapinformationtoboosttheperformanceof
HDMapconstructionforautonomousdriving. MapEX[44]useshistoricallystoredmapinformation
tooptimizetheconstructionofcurrentlocalhigh-precisionmaps. NMP[51]usesaneuralmapprior
toboosttheperformanceofVectorMapNet[38].
Somemoreclosedworkusessatelliteimageinformationtoenhancemapconstruction. SatforHDMap
[23] leverages satellite images as an additional input modality for MapTR [35]. P-MapNet [32]
extractsweaklyalignedSDMapfromOpenStreetMap[4],andencodeitasanadditionalfeaturefor
MapTR,achievingbetterperformance. OurOpenSatMaphasthepotentialtoadvancethisfield. We
takeSatforHDMapasanexample. Weuseintersection-over-union(IoU)asthemetricfollowing
8

semanticmaplearning[34]. LetD ,D ∈RH×W×D bedensepredictionsofshapes,H andW are
1 2
theheightandwidthofthegrid,Disthenumberofcategories. IoUcanbeexpressedasfollows:
|D ∩D |
IoU(D ,D )= 1 2 , (2)
1 2 |D ∪D |
1 2
where|·|isthesizeoftheset. Table3showstheresultsusingSatforHDMap[23]withOpenSatMap.
Theuseofcorrespondingsatelliteimagerysignificantlyenhancedtheperformanceofonlinemap
construction,demonstratingthepotentialsuperiorityofthisapproach.
Table3: EvaluationofsemanticmapsegmentationonnuScenesvalidationset.
Method Divider Crossing Boundary All
HDMapNet[34] 40.6 18.7 39.5 32.9
SatforHDMap[23] 50.2 53.2 49.4 50.9
6 AvailabilityandMaintenance
OpenSatMapiscollectedfromGoogleMaps,whichispubliclyavailable.Accordingtotheregulations
of Google, the use of this dataset is restricted to non-commercial research. Our project page
ishttps://opensatmap.github.io,whichcontainsthefulldatasetwithannotationsandcode
repository.Therepositorycontainsthefull-stacktoolstousethisdataset,includingcodeforcollecting
imagesfromGoogleMaps,documents,baselinemodels,andevaluationtools. Weencouragethe
communitytofurtherexploremoretracksandeffectivemethodsusingOpenSatMap. Thisdataset
willbemaintainedoverthelongtermandcontinuallyiteratedupon.
7 LimitationsandPotentialSocialImpact
OpenSatMaphasthefollowinglimitations. (i)OpenSatMap iscollectedfromGoogleMaps,which
isnotupdatedinrealtime,andcertainareasmaybeoutdatedandnotreflectthecurrentconditions.
Besides, the timing of captured remote sensing images may not be aligned with nuScenes and
Argoversedataset. Althoughwenoticedthispotentialmisalignmentonroadstructuresandaskedthe
annotatorstochecktheconsistencyofroadstructuresbetweenourdataandthedatainthedriving
datasets during annotating process, there are still very few inconsistencies. (ii) High-resolution
(level-20) images in certain areas are not available or may be covered by the cloud, limiting the
diversityofcollectionlocationstosomeextent. (iii)Althoughtheannotatorsarequiteprofessional
andweconductstrictsanitychecks,thesubjectivityofannotatorsmayinevitablyleadtoslightly
inconsistent annotation results since this project employs around 60 annotators. In addition, the
inconsistentannotationcanalsostemfromthedifferenttrainingandexpertiselevelsoftheannotators.
Apotentialsocialimpactisthatitmightcauseasafetyriskfordrivingifthemodelisdirectlytrained
onourdataset,whichcontainsoutdateddataasdiscussedabove.
8 Conclusion
Insummary,weintroduceOpenSatMap,alarge-scale,high-resolution,geographicallydiversesatellite
dataset with detailed annotations and alignment with driving benchmarks. To validate the utility
ofOpenSatMap,weconstructtheinstance-levellinedetectiontrackandprovideabaselineforit.
Moreover,weuseOpenSatMaptoimprovetheperformanceofonlinemapconstruction,whichshows
the great potential of autonomous driving. We believe that our carefully annotated high-quality
OpenSatMapcanserveasthefoundationforvariousapplications,includinglanedetection,city-scale
mapconstruction,andautonomousdriving.
AcknowledgmentsandDisclosureofFunding
ThisworkwassupportedinpartbytheNationalKeyR&DProgramofChina(No. 2022ZD0116500),
theNationalNaturalScienceFoundationofChina(No. U21B2042,No. 62320106010),andinpart
bythe2035InnovationProgramofCAS,andtheInnoHKprogram,andinpartbytheTencentMaps
CollaborativeResearchProject.
9

Checklist
1. Forallauthors...
(a) Dothemainclaimsmadeintheabstractandintroductionaccuratelyreflectthepaper’s
contributionsandscope? [Yes]
(b) Didyoudescribethelimitationsofyourwork? [Yes]SeeinSec.7.
(c) Didyoudiscussanypotentialnegativesocietalimpactsofyourwork? [Yes]Seein
Sec.7
(d) Haveyoureadtheethicsreviewguidelinesandensuredthatyourpaperconformsto
them? [Yes]
2. Ifyouareincludingtheoreticalresults...
(a) Didyoustatethefullsetofassumptionsofalltheoreticalresults? [N/A]Wearenot
includingthese.
(b) Didyouincludecompleteproofsofalltheoreticalresults? [N/A]Wearenotincluding
these.
3. Ifyouranexperiments(e.g. forbenchmarks)...
(a) Didyouincludethecode,data,andinstructionsneededtoreproducethemainexperi-
mentalresults(eitherinthesupplementalmaterialorasaURL)?[Yes]Seeourproject
page.
(b) Didyouspecifyallthetrainingdetails(e.g.,datasplits,hyperparameters,howthey
werechosen)? [Yes]Seethesupplementalmaterial.
(c) Didyoureporterrorbars(e.g.,withrespecttotherandomseedafterrunningexperi-
mentsmultipletimes)? [Yes]SeeinTable2
(d) Didyouincludethetotalamountofcomputeandthetypeofresourcesused(e.g.,type
ofGPUs,internalcluster,orcloudprovider)? [Yes]Seethesupplementalmaterial.
4. Ifyouareusingexistingassets(e.g.,code,data,models)orcurating/releasingnewassets...
(a) Ifyourworkusesexistingassets,didyoucitethecreators? [Yes]
(b) Didyoumentionthelicenseoftheassets? [Yes]
(c) DidyouincludeanynewassetseitherinthesupplementalmaterialorasaURL?[Yes]
Seetheprojectpage.
(d) Didyoudiscusswhetherandhowconsentwasobtainedfrompeoplewhosedatayou’re
using/curating? [Yes]SeeSec.6.
(e) Didyoudiscusswhetherthedatayouareusing/curatingcontainspersonallyidentifiable
informationoroffensivecontent? [Yes]Sec.3.1andSec.6.
5. Ifyouusedcrowdsourcingorconductedresearchwithhumansubjects...
(a) Didyouincludethefulltextofinstructionsgiventoparticipantsandscreenshots,if
applicable? [Yes]SeeSec.3.2.
(b) Did you describe any potential participant risks, with links to Institutional Review
Board(IRB)approvals,ifapplicable? [N/A]Thisworkdoesnotusehumansubjects.
(c) Didyouincludetheestimatedhourlywagepaidtoparticipantsandthetotalamount
spentonparticipantcompensation? [Yes]SeeSec.3.2.
10

InthisSupplementaryMaterial,we:
• Provideadetaileddescriptionofthedatasetfollowingguidesondatasetpublication[26].
• Providethedetailsandresultsoninstance-levellinedetectionandsatellite-enhancedonline
mapconstructionforautonomousdriving.
A OpenSatMapDescription
A.1 Datasheets
A.1.1 Motivation
1. Forwhatpurposewasthedatasetcreated? Wasthereaspecifictaskinmind? Wasthere
aspecificgapthatneededtobefilled? Pleaseprovideadescription.
OpenSatMapiscreatedtoparsefine-grainedroadstructuresfromsatelliteimagesandcan
serveasafoundationforvariousapplications,includingcity-scalemapconstruction,lane
linedetection,andautonomousdriving,etc.. Existingbenchmarks[37,6,18,14]havemade
attemptstohandlethistask. However,theirlimitationsincludingcoarseannotations,low
resolution,smallscaleandunalignmentwithautonomousdrivingbenchmarkspreventthem
fromeffectivelysupportinglarge-scaleandfine-grainedmapconstruction.
2. Whocreatedthedatasetandonbehalfofwhichentity?
ThedatasetwasdevelopedbyaconsortiumofMLresearchersfromCASIA,HKISIand
employeesfromTencentMapslistedintheauthorlist.
3. Whofundedthecreationofthedataset?
This work was supported in part by the National Key R&D Program of China (No.
2022ZD0116500), the National Natural Science Foundation of China (No. U21B2042,
No. 62320106010),andinpartbythe2035InnovationProgramofCAS,andtheInnoHK
program,andinpartbytheTencentMapsCollaborativeResearchProject.
A.1.2 Composition
1. Whatdotheinstancesthatcomprisethedatasetrepresent?
Ourdatasetcontainssatelliteimagesandannotations. Foreachimage,weannotatelane
lineswiththreecategoriesandeightattributes.
2. Howmanyinstancesarethereintotal(ofeachtype,ifappropriate)?
Thereare1806imagesinOpenSatMap19withimagesize2048×2048and1981imagesin
OpenSatMap20withimagesize4096×4096. Foreachimage,weusepolylinestoannotate
lane lines and 8 attributes (color, line type, number of lines, line function, bi-direction,
boundary,occlusionandclearness)foreachline. Thereare446,645linesintotal.
3. Doesthedatasetcontainallpossibleinstancesorisitasample(notnecessarilyrandom)
ofinstancesfromalargerset?
Yes,itcontainsallpossibleinstances.
4. Istherealabelortargetassociatedwitheachinstance?
Yes.
5. Isanyinformationmissingfromindividualinstances?
Yes. InOpenSatMap19,wecannotprovidetheGPSinformationbecauseoftheregulation
inChina. However,thisdoesnotaffecttheuseofourdataset.
6. Arerelationshipsbetweenindividualinstancesmadeexplicit?
Yes. Ourdatasetiswell-organizedandtherelationshipsbetweeninstancesareexplicit.
7. Arethererecommendeddatasplits(e.g.,training,development/validation,testing)?
Yes. Wehavealreadydonethisforuserswhenthedatasetreleases.
8. Arethereanyerrors,sourcesofnoise,orredundanciesinthedataset?
Yes. Noisecomesfromsomepoor-qualityimagesfromGoogleMaps.
9. Isthedatasetself-contained,ordoesitlinktoorotherwiserelyonexternalresources
(e.g.,websites,tweets,otherdatasets)?
Thedatasetisself-contained.
11

10. Doesthedatasetcontaindatathatmightbeconsideredconfidential?
No.
11. Does the dataset contain data that, if viewed directly, might be offensive, insulting,
threatening,ormightotherwisecauseanxiety?
No.
A.1.3 CollectionProcess
1. Howwasthedataassociatedwitheachinstanceacquired? Wasthedatadirectlyob-
servable(e.g., rawtext, movieratings), reportedbysubjects(e.g., surveyresponses), or
indirectlyinferred/derivedfromotherdata(e.g.,part-of-speechtags,model-basedguesses
forageorlanguage)? Ifthedatawasreportedbysubjectsorindirectlyinferred/derivedfrom
otherdata,wasthedatavalidated/verified?
The data is acquired from Google Maps using static public API. The col-
lection process is in accordance with Google Maps terms. Please refer to
https://maps.google.com/help/terms_maps/formoredetails.
2. Whatmechanismsorprocedureswereusedtocollectthedata(e.g.,hardwareappara-
tusesorsensors,manualhumancuration,softwareprograms,softwareAPIs)?
We use one NVIDIA A30 to run a program with the Maps Static API in Google
Maps. We will provide the source code in our GitHub repository. The col-
lection process is in accordance with Google Maps terms. Please refer to
https://maps.google.com/help/terms_maps/formoredetails.
3. Whowasinvolvedinthedatacollectionprocess(e.g.,students,crowdworkers,contrac-
tors)andhowweretheycompensated?
Theauthorsintheauthorlistcollectthedataandaprofessionalremotesensingimagery
labelingteamofapproximately50annotatorslabelthedata. Thetotalcostoflabelingis
about$72,000. Foreachcrowdworker,thehourlyrateis$10.
4. Overwhattimeframewasthedatacollected?
Thedatawascollectedover7weeks,duringtheSpringof2024(March15th,2024through
May10th,2024).
5. Wereanyethicalreviewprocessesconducted(e.g.,byaninstitutionalreviewboard)?
Yes. WeobtainthepubliclyavailableimagesfromGoogleMaps. Googlehasconductedthe
ethicalreviewprocessesforthedata.
A.1.4 Preprocessing/Labeling
1. Wasanypreprocessing/cleaning/labelingofthedatadone?
Yes. Wemanuallycleanedtheimageswithpoorquality(blurred,distorted,spliced,etc. and
withoutroads.).
2. Wasthe“raw”datasavedinadditiontothepreprocessed/cleaned/labeleddata(e.g.,to
supportunanticipatedfutureuses)?
Yes. Wewillprovideitalongwiththereleaseofthedataset.
3. Isthesoftwarethatwasusedtopreprocess/clean/labelthedataavailable?
Theannotatorsusesoftwaretohelptheannotationprocess,andthesoftwareisdeveloped
themselves.
A.1.5 Uses
1. Hasthedatasetbeenusedforanytasksalready?
No,thisdatasethasnotbeenusedforanytasksyet.
2. What(other)taskscouldthedatasetbeusedfor?
It could be used to conduct instance-level line detection, satellite-enhanced online map
constructionforautonomousDriving,super-resolutionimagereconstruction,etc..
3. Aretheretasksforwhichthedatasetshouldnotbeused?
No.
4. Isthereanythingaboutthecompositionofthedatasetorthewayitwascollectedand
preprocessed/cleaned/labeledthatmightimpactfutureuses?
12

Yes. Weonlyannotatedthelanelinesinthedataset,leavingalargeamountofinformation
unlabeled(e.g.,buildings,carsetc.),whichlimitsthefurtherusesofthisdataset. Wehave
alreadydiscussedthisinSec. 7.
A.1.6 Distribution
1. Will the dataset be distributed to third parties outside of the entity (e.g., company,
institution,organization)onbehalfofwhichthedatasetwascreated?
Yes,thedatasetisopentothepublic.
2. Howwillthedatasetbedistributed(e.g.,tarballonwebsite,API,GitHub)?
WeintendtodistributethisdatasetthroughHuggingFaceandtarballonwebsite. Thecode
forbaselineswillbereleasedonGitHub.
3. Whenwillthedatasetbedistributed?
Itwillbedistributedinfall2024.
4. Willthedatasetbedistributedunderacopyrightorotherintellectualproperty(IP)
license,and/orunderapplicabletermsofuse(ToU)?
ThedatasetwillbelicensedunderaCreativeCommonsCC-BY-NC-SA4.0license. Mean-
while,theuseoftheimagesfromGoogleMapsmustrespectthe"GoogleMaps"termsofuse
(https://about.google/brand-resource-center/products-and-services/geo-guidelines/,
https://maps.google.com/help/terms_maps/).
5. HaveanythirdpartiesimposedIP-basedorotherrestrictionsonthedataassociated
withtheinstances?
No.
6. Do any export controls or other regulatory restrictions apply to the dataset or to
individualinstances?
No.
A.1.7 Maintenance
1. Whowillbesupporting/hosting/maintainingthedataset?
Alltheauthorswillbesupporting/hosting/maintainingthedatasetinthelongterm.
2. Howcantheowner/curator/managerofthedatasetbecontacted(e.g.,emailaddress)?
Throughourprojectpagehttps://opensatmap.github.io/whichcontainsouremail
addressesorGitHubissues.
3. Isthereanerratum?
Notyet.
4. Willthedatasetbeupdated?
Yes,thedatasetswillbeupdatedwhenevernecessarytoensureaccuracy,andannounce-
ments will be made accordingly. All the updates can be found in our project page
https://opensatmap.github.io/.
5. Ifthedatasetrelatestopeople,arethereapplicablelimitsontheretentionofthedata
associatedwiththeinstances?
Notapplicable.
6. Willolderversionsofthedatasetcontinuetobesupported/hosted/maintained?
Yes,olderversionsofthedatasetwillcontinuetobesupported/hosted/maintained.
7. Ifotherswanttoextend/augment/buildon/contributetothedataset,isthereamecha-
nismforthemtodoso?
Yes. TheycancontactusfromourprojectpageorpostaGitHubissue.
A.2 DatasetAnnotationDocumentation
Inthissubsection,weprovideadetaileddescriptionofourinstance-levelandimage-levelannotation
rules,whichhelpsthedatasetconsumerstobetterunderstandanduseourdataset.
13

A.2.1 Overview
OpenSatMapisahigh-resolution,geographicallydiverse,large-scale,satelliteimagedatasetwithfine-
grainedinstance-levelannotations. Besides,inordertoadvancethemapconstructioninautonomous
driving,OpenSatMapcoverstheregionsofnuScenes[8]andArgoverse2[11]datasets.
A.2.2 Instance-levelAnnotationRules
We use vectorized polylines to represent a line instance. We first categorize all lines into three
categories: curb,laneline,andvirtualline. Acurbistheboundaryofaroad. Lanelinesarethose
visiblelinesformingthelanes. Avirtuallinemeansnolanelineorcurbhere,butlogicallythere
shouldbeaboundarytoformafulllane.
Eachlineisassignedacoupleofattributesbasedonitsappearanceandfunctionalities. Specifically,
thereare8attributesasfollows:
• Color: White,Yellow,Others,None.
• Linetype: Solidline,Thicksolidline,Dashedline,Shortdashedline,Others,None.
• Numberoflines: Singleline,Doubleline,Others,None.
• Function: Chevronmarkings,Noparking,Decelerationlane,Buslane,Others,Tidallane,
Parkingspaces,Vehiclestagingarea,Guidanceline,Lane-borrowingarea.
• Bidireciton: True,False.
• Boundary: True,False.
• Occlusion: Noocclusion,Minorocclusion,Majorocclusion.
• Clearness: Clear,Fuzzy.
Notethatthereisnoman-madevisiblelineoncurbsandvirtuallines,soweannotatetheircolors,
linetypes,numbersoflines,andfunctionsasNone. Intermsoflinecolors,linetypes,numbersof
lines,functions,boundaries,andclearness,theyareapparentandeasytodistinguish.
Inthefollowing,wegivemoredetailsaboutbidirectionandocclusion. Forbidirection,theorderof
thepointsinthepolylinesdefinesthelinedirection. Wecaneasilydeterminethedirectionofthelines
bytrafficflow,arrows,etc. However,itishardtotellthedirectionsofsomelines,e.g.,thecenterline
ofaroad,whichisbidirectional. Therefore,wedesignbidirectionattributetohandlethiscondition.
Forocclusion,weusetheratioofthelinestobeblockedbytrees,cars,andbuildings. Whentheratio
isgreaterthan50%,wegiveitmajorocclusion. Whentheratioissmallerthan50%,welabelminor
occlusion. Whenthelineisfullyvisible,welabelnoocclusion.
Afterdefiningthelineattributes,wegivethedefinitionofeachinstanceusingthefollowingrules.
Although we have already talked about the definition of the instance in Sec. 3.2, here is a more
detaileddiscussionforbetterunderstanding. Thedetailedrulesofeachtagareshownbelow. (i)
Different instances have different attributes. For example, if a solid line becomes a dashed line,
wecutthelineintotwoinstances. PleaserefertoFigure5aforanexample. (ii)Whenalinefork
ormerge(e.g.,“Y”-shapepoint),webreakitintothreeinstances. PleaserefertoFigure5bforan
example.
Inadditiontothesegeneralizedrulesabove,therearesomerulesforspecificsituations.
(i)Occlusioninference. Ifalineispartiallyoccludedbybuildings,trees,andvehiclesbutitscomplete
shapecanbeinferredwithhighconfidence,wewillannotateit. Fullyoccludedlinesarenotlabeled.
However,theoverpassisaspecialcaseandwewilldiscussitlater.
(ii)Overpass. Whenthereisamulti-levelinterchange,theupper-leveloverpasswillobscurethelane
linesonthelowerlevel. Althoughinthiscase,theunderlyinglanelinescanbeinferred,theportion
coveredbytheupperleveloftheinterchangeisnotlabeledtoavoidconflictswiththeupperones.
Besides,theloweroverpassbreaksoffatthispointfortwoinstances.
14

Attribute Change
Overpass Cut Off
Fork & Merge Occlusions
Inference
(a) Attribute change. (b) Lines fork and merge. (c) Overpass cut off. (d) Occlusions inference.
Figure10: Definitionofinstances(zoominforbestviewing). In(a),achangeoflinetyperesults
intwoinstancessharingthesamepoint. In(b),alineshouldbedividedintothreeinstanceswhen
itisforkedormerged. (c)showsanexampleofmulti-levelinterchange. (d)showstheannotation
inferencescausedbytheocclusionofthebuildings.
(a) Dense. (b) Moderate. (c) Sparse.
Figure11: Vehicledensityexamples.
A.2.3 Image-levelAnnotationRules
We provide OpenSatMap20 with 4 additional image-level tags including image clarity, vehicle
density,settlementtypeandspecialroadstructuretodescribegeneralinformationofeachimage. The
followingaredetailedrulesforeachtag.
Imageclarity. Thisattributeisusedtodescribetheclarityoftheimage.
• Completelyclear: Clearviewoflanelinesandsurroundings.
• Partiallyclear: Somelanelinesareclear,someareblurryorhaveghosting,etc. Lessthan
30%ofthelanelinesintheimageareblurred.
• Notclear: Morethan30%oftheroadsareunclear. Forimageswiththistag,wewillnot
annotatethemandremovethemfromOpenSatMap.
Vehicledensity. Wehavethreelevelstodescribethevehicledensityofanimage. Figure11shows
anexampleofeachcase.
• Dense: Thedistancebetweencarsislessthan5vehiclelengths.
• Moderate: Therearesomecarsontheroadandthedistancebetweencarsisgreaterthan5
vehiclelengths.
• Sparse: Onlylessthan20%ofmajorroadshavecarsandtheresthavenocars.
Settlement type. Settlement type is used to describe the surroundings of the road. It includes
suburban,ruralandurban. Figure12showsanexampleofeachcase.
• Urban: Thesurroundingsareallhighrisesandofficebuildings.
• Suburban: Aformofurbansettlementwithmediumpopulationdensity,itcanbeseenasthe
middlegroundbetweencityandcountrylife.
15

(a) Urban. (b) Suburban. (c) Rural.
Figure12: Settlementtypeexamples.
(a) Flyover. (b) Cross-river bridge. (c) Roundabout (d) Winding road.
Figure13: Specialroadstructureexamples.
• Rural: Ahumansettlementwithalowpopulationdensity. Thenumberofbuildingsisthe
leastofthethree.
Special road structure. This tag describes the special road structures of an image and multiple
specialstructurescanexistinoneimage. Wedefinefourspecialroadstructuresincludingroundabout,
flyover(overpass),windingroadandcross-riverbridge. Figure13showsanexampleofeachcase.
B DetailsofBaselineMethods
B.1 Instance-levelLineDetection
Implementationdetails. WeuseMMSegmentation[16]toconductthesemanticsegmentation. For
OpenSatMap19,wecuteachimageinto512×512andforOpenSatMap20,wecuttheminto1024
×1024. Aftercuttingprocess,weresizeeachimageinto2048×2048,i.e.,weuse"pseudolevel-21
images"forsegmentation. Inthe"pseudolevel-21images",wesetthelinewidthas6pixel. We
followthesettingofSegNeXt[27]tinyandusecrossentroylossanddicelossaslossfunction. All
theexperimentsareconductedon8RTX3090GPUs. Table4showsthehyperparametersweuse.
Inourbaselinemethod,weuselinecategories(laneline,curb,background,virtualline)andline
types (solid line, thick solid line, dashed line, short dashed line and others) to conduct semantic
segmentationandthenumberofcategoriesiseight. Wegetthisnumberaccordingtoourdefinition
ofinstances,i.e.,whenoneattributechanges,weshouldbreakthelineintotwoinstances. Withthis
definition,wefurtherfindonlylinetypesandlinecategoriesmaychangebetweentwoconnected
linesegments,e.g.,asolidlineturnsintoadashedlineoravirtuallinebreaksthecurb. Soweonly
considertheselinecategoriesandlinetypesinoursemanticsegmentationmodel. Otherattributesdo
notinfluencethedefinitionofinstancesandarenotusedinthisbenchmark.
B.2 Satellite-enhancedOnlineMapConstructionforAutonomousDriving
In this subsection, we demonstrate that our dataset could help the online map construction for
autonomousdriving.
16

Table4: Hyperparametersininstance-levellinedetectiontrack.
Config Value
optimizer AdamW
learningrate 8e-5
weightdecay 0.01
momentum β ,β =0.9,0.999
1 2
batchsize 8
learningrateschedule cosinedecay
warmupiterations 400
trainingiterations 40000
augmentation RandomFlip
droppath 0.1
classweightinCEloss 1,20,30,40
Task definition. We follow the setting of semantic map learning, which was first proposed by
HDMapNet[34]. Inputsarecameraimages I ofanautonomousdrivingvehicleand outputsare
vectorizedmapelementsMaroundthevehicle. SatforHDMap[23]addsthecorrespondingsatellite
imagesofeachsampleasadditionalinputI ∈ RH×W×3 andimprovestheperformance,where
S
H ×W indicatestheinputresolution. Itisahyperparameteranddecidedbytheregionofasatellite
map tile (e.g., 60m×30m). Based on SatforHDMap, we add the mask of the satellite images
I ∈RH×W asanadditionalinput.
MS
Implementationdetails. WeusethemodelfromSatforHDMap[23]andaddanadditionalbranch
toprocessthemaskinput. Alltheexperimentsonlyusethecaremaimagesandadditionalsatellite
imagesasinput. Wesetthesatelliteimagesamplingareaas60m×30m,andthecorresponding
satelliteimagestilesizeisshowninTable5. Table6showsthehyperparametersforthistrack.
Table5: ResolutionofsatellitemaptilesinnuScenes.
Region Resolution
BostonSeaport 545×273
SingaporeOneNorth 403×202
SingaporeQueenstown 403×202
SingaporeHollandVillage 404×202
Table6: Hyperparametersinsatellite-enhancedonlinemapconstructiontrack.
Config Parameters
optimizer Adam
learningrate 0.0016
weightdecay 1e-7
momentum β ,β =0.9,0.999
1 2
batchsize 32
trainingepochs 30
References
[1] GoogleMaps. https://maps.google.com.
[2] Imagesegmentationwithwatershedalgorithm.https://docs.opencv.org/3.4/d3/db4/tutorial_py_watershed.html.
[3] Noaafisheriesstellersealionpopulationcount|kaggle.https://www.kaggle.com/c/noaa-fisheries-steller-sea-lion-population-count.
[4] OpenStreetMap. https://www.openstreetmap.org.
[5] QGIS. https://qgis.org/en/site/.
[6] FavyenBastani,SongtaoHe,SofianeAbbar,MohammadAlizadeh,HariBalakrishnan,SanjayChawla,
SamMadden,andDavidDeWitt. Roadtracer:Automaticextractionofroadnetworksfromaerialimages.
InProceedingsoftheIEEEconferenceoncomputervisionandpatternrecognition,pages4720–4728,
2018.
[7] MartinBüchner,JannikZürn,Ion-GeorgeTodoran,AbhinavValada,andWolframBurgard. Learningand
aggregatinglanegraphsforurbanautomateddriving. InProceedingsoftheIEEE/CVFConferenceon
ComputerVisionandPatternRecognition,pages13415–13424,2023.
17

[8] HolgerCaesar,VarunBankiti,AlexHLang,SourabhVora,VeniceErinLiong,QiangXu,AnushKrishnan,
YuPan,GiancarloBaldan,andOscarBeijbom.nuscenes:Amultimodaldatasetforautonomousdriving.In
ProceedingsoftheIEEE/CVFconferenceoncomputervisionandpatternrecognition,pages11621–11631,
2020.
[9] NicolasCarion,FranciscoMassa,GabrielSynnaeve,NicolasUsunier,AlexanderKirillov,andSergey
Zagoruyko. End-to-endobjectdetectionwithtransformers. InEuropeanconferenceoncomputervision,
pages213–229.Springer,2020.
[10] JavieraCastillo-Navarro,BertrandLeSaux,AlexandreBoulch,NicolasAudebert,andSébastienLefèvre.
Semi-supervisedsemanticsegmentationinearthobservation:Theminifrancesuite,datasetanalysisand
multi-tasknetworkstudy. MachineLearning,111(9):3125–3160,2022.
[11] Ming-FangChang, JohnLambert, PatsornSangkloy, JagjeetSingh, SlawomirBak, AndrewHartnett,
DeWang,PeterCarr,SimonLucey,DevaRamanan,etal. Argoverse:3dtrackingandforecastingwith
richmaps. InProceedingsoftheIEEE/CVFconferenceoncomputervisionandpatternrecognition,pages
8748–8757,2019.
[12] HaoChenandZhenweiShi. Aspatial-temporalattention-basedmethodandanewdatasetforremote
sensingimagechangedetection. RemoteSensing,12(10),2020.
[13] BowenCheng, IshanMisra, AlexanderGSchwing, AlexanderKirillov, andRohitGirdhar. Masked-
attentionmasktransformerforuniversalimagesegmentation. InProceedingsoftheIEEE/CVFconference
oncomputervisionandpatternrecognition,pages1290–1299,2022.
[14] Guangliang Cheng, Ying Wang, Shibiao Xu, Hongzhen Wang, Shiming Xiang, and Chunhong Pan.
Automaticroaddetectionandcenterlineextractionviacascadedend-to-endconvolutionalneuralnetwork.
IEEETransactionsonGeoscienceandRemoteSensing,55(6):3322–3337,2017.
[15] MangTikChiu,XingqianXu,YunchaoWei,ZilongHuang,AlexanderGSchwing,RobertBrunner,Hrant
Khachatrian,HovnatanKarapetyan,IvanDozier,GregRose,etal.Agriculture-vision:Alargeaerialimage
databaseforagriculturalpatternanalysis.InProceedingsoftheIEEE/CVFConferenceonComputerVision
andPatternRecognition,pages2828–2838,2020.
[16] MMSegmentationContributors. MMSegmentation: Openmmlabsemanticsegmentationtoolboxand
benchmark. https://github.com/open-mmlab/mmsegmentation,2020.
[17] RodrigoCayeDaudt,BertrLeSaux,AlexandreBoulch,andYannGousseau. Urbanchangedetection
formultispectralearthobservationusingconvolutionalneuralnetworks. InIGARSS2018-2018IEEE
InternationalGeoscienceandRemoteSensingSymposium,pages2115–2118,2018.
[18] IlkeDemir,KrzysztofKoperski,DavidLindenbaum,GuanPang,JingHuang,SaikatBasu,ForestHughes,
DevisTuia,andRameshRaskar. Deepglobe2018:Achallengetoparsetheearththroughsatelliteimages.
InProceedingsoftheIEEEConferenceonComputerVisionandPatternRecognitionWorkshops,pages
172–181,2018.
[19] JianDing,NanXue,YangLong,Gui-SongXia,andQikaiLu. Learningroitransformerfordetecting
orientedobjectsinaerialimages. arXivpreprintarXiv:1812.00155,2018.
[20] JianDing,NanXue,Gui-SongXia,XiangBai,WenYang,MichaelYang,SergeBelongie,JieboLuo,
MihaiDatcu,MarcelloPelillo,andLiangpeiZhang. Objectdetectioninaerialimages: Alarge-scale
benchmarkandchallenges. IEEETransactionsonPatternAnalysisandMachineIntelligence,pages1–1,
2021.
[21] MarkEveringham,LucVanGool,ChristopherKIWilliams,JohnWinn,andAndrewZisserman. The
pascalvisualobjectclasses(voc)challenge. InternationalJournalofComputerVision,88(2):303–338,
2010.
[22] LipengGao,YiqingZhou,JiangtaoTian,andWenjingCai. Ddctnet:Adeformableanddynamiccross
transformernetworkforroadextractionfromhighresolutionremotesensingimages. IEEETransactions
onGeoscienceandRemoteSensing,2024.
[23] WenjieGao,JiaweiFu,YanqingShen,HaodongJing,ShitaoChen,andNanningZheng. Complementing
onboardsensorswithsatellitemap:Anewperspectiveforhdmapconstruction,2024.
[24] VivienSainteFareGarnotandLoicLandrieu. Panopticsegmentationofsatelliteimagetimeserieswith
convolutionaltemporalattentionnetworks. InProceedingsoftheIEEE/CVFInternationalConferenceon
ComputerVision,pages4872–4881,2021.
18

[25] JanGasienica-Jozkowy,MateuszKnapik,andBogusławCyganek.Anensembledeeplearningmethodwith
optimizedweightsfordrone-basedwaterrescueandsurveillance. IntegratedComputer-AidedEngineering,
28(3):221–235,2021.
[26] Timnit Gebru, Jamie Morgenstern, Briana Vecchione, Jennifer Wortman Vaughan, Hanna Wallach,
HalDauméIii,andKateCrawford. Datasheetsfordatasets. CommunicationsoftheACM,64(12):86–92,
2021.
[27] Meng-HaoGuo,Cheng-ZeLu,QibinHou,ZhengningLiu,Ming-MingCheng,andShi-MinHu. Segnext:
Rethinkingconvolutionalattentiondesignforsemanticsegmentation. AdvancesinNeuralInformation
ProcessingSystems,35:1140–1156,2022.
[28] KaimingHe,GeorgiaGkioxari,PiotrDollár,andRossGirshick. Maskr-cnn. InProceedingsoftheIEEE
internationalconferenceoncomputervision,pages2961–2969,2017.
[29] SongtaoHeandHariBalakrishnan. Lane-levelstreetmapextractionfromaerialimagery. InProceedings
oftheIEEE/CVFWinterConferenceonApplicationsofComputerVision,pages2080–2089,2022.
[30] SongtaoHe,FavyenBastani,SatvatJagwani,MohammadAlizadeh,HariBalakrishnan,SanjayChawla,
MohamedMElshrif,SamuelMadden,andMohammadAminSadeghi. Sat2graph:Roadgraphextraction
throughgraph-tensorencoding. InComputerVision–ECCV2020:16thEuropeanConference,Glasgow,
UK,August23–28,2020,Proceedings,PartXXIV16,pages51–67.Springer,2020.
[31] PatrickHelber,BenjaminBischke,AndreasDengel,andDamianBorth. Eurosat:Anoveldatasetanddeep
learningbenchmarkforlanduseandlandcoverclassification. IEEEJournalofSelectedTopicsinApplied
EarthObservationsandRemoteSensing,12(7):2217–2226,2019.
[32] ZhouJiang,ZhenxinZhu,PengfeiLi,Huan-angGao,TianyuanYuan,YongliangShi,HangZhao,andHao
Zhao. P-mapnet:Far-seeingmapgeneratorenhancedbybothsdmapandhdmappriors. arXivpreprint
arXiv:2403.10521,2024.
[33] DariusLam,RichardKuzma,KevinMcGee,SamuelDooley,MichaelLaielli,MatthewKlaric,Yaroslav
Bulatov, and Brendan McCord. xview: Objects in context in overhead imagery. arXiv preprint
arXiv:1802.07856,2018.
[34] QiLi,YueWang,YilunWang,andHangZhao. Hdmapnet:Anonlinehdmapconstructionandevaluation
framework. In2022InternationalConferenceonRoboticsandAutomation(ICRA),pages4628–4634.
IEEE,2022.
[35] BenchengLiao,ShaoyuChen,XinggangWang,TianhengCheng,QianZhang,WenyuLiu,andChang
Huang.Maptr:Structuredmodelingandlearningforonlinevectorizedhdmapconstruction.arXivpreprint
arXiv:2208.14437,2022.
[36] Tsung-YiLin,MichaelMaire,SergeBelongie,JamesHays,PietroPerona,DevaRamanan,PiotrDollár,
andCLawrenceZitnick. Microsoftcoco:Commonobjectsincontext. InComputerVision–ECCV2014:
13thEuropeanConference,Zurich,Switzerland,September6-12,2014,Proceedings,PartV13,pages
740–755.Springer,2014.
[37] YahuiLiu, JianYao, XiaohuLu, MenghanXia, XingboWang, andYuanLiu. Roadnet: Learningto
comprehensivelyanalyzeroadnetworksincomplexurbanscenesfromhigh-resolutionremotelysensed
images. IEEETransactionsonGeoscienceandRemoteSensing,57(4):2043–2056,2018.
[38] Yicheng Liu, Tianyuan Yuan, Yue Wang, Yilun Wang, and Hang Zhao. Vectormapnet: End-to-end
vectorizedhdmaplearning. InInternationalconferenceonmachinelearning.PMLR,2023.
[39] VolodymyrMnih. MachineLearningforAerialImageLabeling. PhDthesis,UniversityofToronto,2013.
[40] Sorour Mohajerani and Parvaneh Saeedi. Cloud and cloud shadow segmentation for remote sensing
imageryviafilteredjaccardlossfunctionandparametricaugmentation. IEEEJournalofSelectedTopicsin
AppliedEarthObservationsandRemoteSensing,14:4254–4266,2021.
[41] MariaPapadomanolaki,MariaVakalopoulou,andKonstantinosKarantzalos. Adeepmultitasklearning
framework coupling semantic segmentation and fully convolutional lstm networks for urban change
detection. IEEETransactionsonGeoscienceandRemoteSensing,59(9):7651–7668,2021.
[42] Maryam Rahnemoonfar, Tashnim Chowdhury, Argho Sarkar, Debvrat Varshney, Masoud Yari, and
Robin Roberson Murphy. Floodnet: A high resolution aerial imagery dataset for post flood scene
understanding. IEEEAccess,9:89644–89654,2021.
19

[43] Gencer Sumbul, Marcela Charfuelan, Begüm Demir, and Volker Markl. Bigearthnet: A large-scale
benchmarkarchiveforremotesensingimageunderstanding. InIGARSS2019-2019IEEEInternational
GeoscienceandRemoteSensingSymposium,pages5901–5904.IEEE,2019.
[44] RémySun,LiYang,DianeLingrand,andFrédéricPrecioso. Mindthemap!accountingforexistingmap
informationwhenestimatingonlinehdmapsfromsensordata. arXivpreprintarXiv:2311.10517,2023.
[45] ShiqiTian,AilongMa,ZhuoZheng,andYanfeiZhong. Hi-ucd:Alarge-scaledatasetforurbansemantic
changedetectioninremotesensingimagery. arXivpreprintarXiv:2011.03247,2020.
[46] AdamVanEtten,DanielHogan,JesusMartinezManso,JacobShermeyer,NicholasWeir,andRyanLewis.
Themulti-temporalurbandevelopmentspacenetdataset. InProceedingsoftheIEEE/CVFConferenceon
ComputerVisionandPatternRecognition,pages6398–6407,2021.
[47] AdamVanEtten,DaveLindenbaum,andToddMBacastow. Spacenet: Aremotesensingdatasetand
challengeseries. arXivpreprintarXiv:1807.01232,2018.
[48] Haochen Wang, Junsong Fan, Yuxi Wang, Kaiyou Song, Tong Wang, and ZHAO-XIANG ZHANG.
Droppos: Pre-training vision transformers by reconstructing dropped positions. Advances in Neural
InformationProcessingSystems,36,2023.
[49] Junjue Wang, Zhuo Zheng, Ailong Ma, Xiaoyan Lu, and Yanfei Zhong. Loveda: A remote sensing
land-coverdatasetfordomainadaptivesemanticsegmentation. arXivpreprintarXiv:2110.08733,2021.
[50] Gui-SongXia,XiangBai,JianDing,ZhenZhu,SergeBelongie,JieboLuo,MihaiDatcu,MarcelloPelillo,
andLiangpeiZhang. Dota: Alarge-scaledatasetforobjectdetectioninaerialimages. InTheIEEE
ConferenceonComputerVisionandPatternRecognition(CVPR),June2018.
[51] XuanXiong,YichengLiu,TianyuanYuan,YueWang,YilunWang,andHangZhao. Neuralmapprior
forautonomousdriving. InProceedingsoftheIEEE/CVFConferenceonComputerVisionandPattern
Recognition,pages17535–17544,2023.
[52] JiaweiYao,XiaochaoPan,TongWu,andXiaofengZhang.Buildinglane-levelmapsfromaerialimages.In
ICASSP2024-2024IEEEInternationalConferenceonAcoustics,SpeechandSignalProcessing(ICASSP),
pages3890–3894.IEEE,2024.
[53] AndiZang,RunshengXu,ZichenLi,andDavidDoria. Laneboundarygeometryextractionfromsatellite
imagery. arXivpreprintarXiv:2002.02362,2020.
[54] QiqiZhu,YananZhang,LizengWang,YanfeiZhong,QingfengGuan,XiaoyanLu,LiangpeiZhang,and
DerenLi. Aglobalcontext-awareandbatch-independentnetworkforroadextractionfromvhrsatellite
imagery. ISPRSJournalofPhotogrammetryandRemoteSensing,175:353–365,2021.
20