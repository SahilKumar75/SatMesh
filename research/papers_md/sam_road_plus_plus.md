Towards Satellite Image Road Graph Extraction: A Global-Scale Dataset and A
Novel Method
PanYin1*,KaiyuLi1*,XiangyongCao1†,JingYao2,LeiLiu3,XueruBai3,FengZhou3,DeyuMeng1
1Xi’anJiaotongUniversity 2ChineseAcademyofSciences 3XidianUniversity
yinpan 22@stu.xjtu.edu.cn, likyoo.ai@gmail.com, caoxiangyong@mail.xjtu.edu.cn
yaojing@aircas.ac.cn, leiliu@xidian.edu.cn, xrbai@xidian.edu.cn
fzhou@mail.xidian.edu.cn, dymeng@mail.xjtu.edu.cn
[lon, lat] data of
selected cities
Collect satellite data Collect road graph data
from Google Earth from OpenStreetMap
Manual filtration
Global-Scale dataset
(a) (b)
Figure1. (a)ThecollectionpipelineofourGlobal-Scaledataset;(b)Theworldmapshowingtheregionlocationofthecollectedimages
intheGlobal-Scaledataset.
Abstract Road++method,particularlyhighlightingitssuperiorpre-
dictivepowerinunseenregions. Thedatasetandcodeare
Recently,roadgraphextractionhasgarneredincreasingat- availableathttps://github.com/earth-insights/samroadplus.
tention due to its crucial role in autonomous driving, nav-
igation,etc. However,accuratelyandefficientlyextracting
road graphs remains a persistent challenge, primarily due 1.Introduction
to the severe scarcity of labeled data. To address this lim-
itation, we collect a global-scale satellite road graph ex- Inrecentyears,dailytravelhasincreasinglyreliedonnav-
tractiondataset,i.e. Global-Scaledataset. Specifically,the igation systems [32], particularly with the advent of au-
Global-Scale dataset is ∼ 20× larger than the largest ex- tonomous driving technology [21], which has greatly en-
istingpublicroadextractiondatasetandspansover13,800 hanced convenience in everyday life [35, 49]. These ad-
km2 globally. Additionally,wedevelopanovelroadgraph vancements demand higher accuracy and real-time per-
extractionmodel,i.e. SAM-Road++,whichadoptsanode- formance in extracting road graphs from satellite images
guided resampling method to alleviate the mismatch issue [6, 42]. Existing approaches to end-to-end road graph ex-
between training and inference in SAM-Road [15], a pio- traction can be categorized into two main types: iterative
neeringstate-of-the-artroadgraphextractionmodel. Fur- methods[2,45,46]andglobal-basedmethods[13,15]. It-
thermore,weproposeasimpleyeteffective“extended-line” erativemethodsgeneratearoadgraphpointbypointfrom
strategyinSAM-Road++tomitigatetheocclusionissueon the edges of an image. While effective in road graph ex-
theroad. Extensiveexperimentsdemonstratethevalidityof traction,thisstep-by-stepconnectionprocesscanleadtoer-
thecollectedGlobal-ScaledatasetandtheproposedSAM- roraccumulationandsignificantcomputationalburdens. In
contrast,global-basedmethodscandirectlyproduceacom-
*Equalcontribution.†Correspondingauthor. pleteroadgraph,addressingthelimitationsofiterativeap-
1
4202
voN
32
]VC.sc[
1v33761.1142:viXra

proaches. For instance, SAM-Road [15] performs global works. Theout-of-domainsetconsistsofdatafromregions
roadgraphpredictionintwostages: roadsegmentationand notincludedinthetrainingset,enhancingtherobustnessof
relationshippredictionbetweenkeypoints. However,these ourevaluations. Insummary,themaincontributionsofthis
| twostagesareuncoupledduringtraining,thefirststageem- |              |       |                   |       |       |               |         | workarethreefold:                                  |     |             |     |      |              |     |
| ---------------------------------------------------- | ------------ | ----- | ----------------- | ----- | ----- | ------------- | ------- | -------------------------------------------------- | --- | ----------- | --- | ---- | ------------ | --- |
| ploys a                                              | conventional |       | road segmentation |       | model | to            | capture |                                                    |     |             |     |      |              |     |
|                                                      |              |       |                   |       |       |               |         | • Weestablishanovelroadgraphextractionmodel,namely |     |             |     |      |              |     |
| the road                                             | mask,        | while | the second        | stage | uses  | node informa- |         |                                                    |     |             |     |      |              |     |
|                                                      |              |       |                   |       |       |               |         | SAM-Road++,                                        |     | by coupling | the | road | segmentation | and |
tionfromthegroundtruthtotrainaclassifierfornodecon-
|     |     |     |     |     |     |     |     | nodeconnectivitypredictionsub-networksasawhole. |     |     |     |     |     | In  |
| --- | --- | --- | --- | --- | --- | --- | --- | ----------------------------------------------- | --- | --- | --- | --- | --- | --- |
nectivity. Thisleadstoamismatchduringinference,asthe SAM-Road++,anode-guidedresamplingstrategyisably
classifier’sinputsarebasedonkeypointsselectedfromthe
introducedtoaddressthemismatchproblembetweenthe
predictedroadmaskratherthanthetrainingdata.
trainingandinferencephasesforthefirsttime.
Totacklethismismatchissue,weproposeanovel“node • To tackle the issue of road occlusion in satellite images,
sampling”strategycallednode-guidedresampling. Instead weproposeanovelextended-linestrategythatutilizesthe
ofdirectlyusinglabelednodesfromthegroundtruthduring correlationbetweenresampledkeynodestofacilitatethe
classifier training, we resample nodes from the predicted identificationandextractionofconnectedroads.
roadmaskthatcorrespondtothecoordinateswiththehigh- • We curate a new benchmark dataset for road extraction,
estprobabilitynearthelabelednodes.Thisapproachallows Global-Scale, which contains the latest satellite images
the classifier to leverage training experiences more effec- and faithful road graph maps with larger data volumes,
tively,resultingingreaterconsistencybetweenthetraining broader coverage, and more diverse scenes, enabling a
and inference processes. Additionally, we recognize that more comprehensive evaluation of road extraction tasks
occlusionpresentsasignificantchallengeinroadgraphex- forthecommunity.
| traction | [47]. | Since models |     | can only | extract | information |     |     |     |     |     |     |     |     |
| -------- | ----- | ------------ | --- | -------- | ------- | ----------- | --- | --- | --- | --- | --- | --- | --- | --- |
fromasingleoverheadviewinsatelliteimages,accurately 2.RelatedWork
| determining | the | connectivity |     | of road | nodes | becomes | diffi- |     |     |     |     |     |     |     |
| ----------- | --- | ------------ | --- | ------- | ----- | ------- | ------ | --- | --- | --- | --- | --- | --- | --- |
2.1.ExistingRoadExtractionDatasets
| cult when        | occlusions |                                      | (e.g., | trees, shadows, |     | etc.) | obstruct |               |            |          |     |        |         |          |
| ---------------- | ---------- | ------------------------------------ | ------ | --------------- | --- | ----- | -------- | ------------- | ---------- | -------- | --- | ------ | ------- | -------- |
| visibility[3,9]. |            | Totacklethischallenge,weaimtoprovide |        |                 |     |       |          |               |            |          |     |        |         |          |
|                  |            |                                      |        |                 |     |       |          | Existing road | extraction | datasets |     | can be | divided | into two |
theclassifierwithmorecontextualinformationforidentify-
|              |         |     |              |     |          |      |           | categories: | segmentation-labeled |     |     | datasets | [8, 30, | 31, 51] |
| ------------ | ------- | --- | ------------ | --- | -------- | ---- | --------- | ----------- | -------------------- | --- | --- | -------- | ------- | ------- |
| ing occluded | scenes. |     | Our strategy |     | is based | on a | straight- |             |                      |     |     |          |         |         |
andgraph-labeleddatasets[13,40].
| forward | assumption: |     | if road | lines | exist on | either | side of |                      |     |      |             |     |            |        |
| ------- | ----------- | --- | ------- | ----- | -------- | ------ | ------- | -------------------- | --- | ---- | ----------- | --- | ---------- | ------ |
|         |             |     |         |       |          |        |         | Segmentation-labeled |     | data | are typical |     | image-mask | pairs. |
twoneighboringnodesalongastraightroad,itislikelythat
|             |              |           |                  |                 |           |          |         | The Massachusetts |               | [31] dataset | covers      | a        | variety | of scenes |
| ----------- | ------------ | --------- | ---------------- | --------------- | --------- | -------- | ------- | ----------------- | ------------- | ------------ | ----------- | -------- | ------- | --------- |
| a road also | connects     |           | these two        | nodes.          | Motivated |          | by this |                   |               |              |             |          |         |           |
|             |              |           |                  |                 |           |          |         | in urban          | and rural     | areas,       | with rich   | terrain  | and     | landform  |
| assumption, | we           | introduce | an               | “extended-line” |           | strategy | that    |                   |               |              |             |          |         |           |
|             |              |           |                  |                 |           |          |         | features.         | The DeepGlobe |              | [8] dataset | provides |         | more than |
| utilizes    | the extended |           | line information |                 | between   | two      | nodes   |                   |               |              |             |          |         |           |
10,000satelliteimages,coveringurban,rural,coastline,and
asanadditionalcriterionfordeterminingroadconnectivity.
|              |     |       |           |          |     |           |        | rainforestsinThailand,Indonesia,andIndia. |     |     |     |     | However,due |     |
| ------------ | --- | ----- | --------- | -------- | --- | --------- | ------ | ----------------------------------------- | --- | --- | --- | --- | ----------- | --- |
| This enables | the | model | to better | navigate |     | occlusion | issues |                                           |     |     |     |     |             |     |
tothelackofvectorinformation,thesedatasetsarenotsuit-
incomplexenvironments.
ableforroadgraphextractiontasks.
| Beyond  | the        | algorithms, |     | another | bottleneck  | constrain- |     | Graph-labeled |          | data     |         |          |           |          |
| ------- | ---------- | ----------- | --- | ------- | ----------- | ---------- | --- | ------------- | -------- | -------- | ------- | -------- | --------- | -------- |
|         |            |             |     |         |             |            |     |               |          | provides | vector  | graphs   | of        | the road |
| ing the | road graph | extraction  |     | task is | the limited | availabil- |     |               |          |          |         |          |           |          |
|         |            |             |     |         |             |            |     | network.      | SpaceNet | [40]     | dataset | is first | presented | in the   |
ity of data. The most commonly used datasets in existing SpaceNetChallenge. AslistedinTab.1,itcontainsimages
roadgraphextractionmethods,suchasCity-Scale[13]and
thatareonly400×400insizeandcovermainlyLasVegas,
SpaceNet[40],areconstrainedbyeitherthenumberofim- Paris,andShanghai. However,thecoverageofSpaceNetis
ages or their locations, focusing primarily on urban roads limitedtourbanroads,lackingdescriptionsofcomplexter-
| [29]. This | limited | data | volume | and | diversity | lead | to two |                                         |     |     |     |     |            |     |
| ---------- | ------- | ---- | ------ | --- | --------- | ---- | ------ | --------------------------------------- | --- | --- | --- | --- | ---------- | --- |
|            |         |      |        |     |           |      |        | rainslikefarmlandandmountainousregions. |     |     |     |     | Ontheother |     |
mainissues: 1)unfaithfulevaluationsofalgorithmsand2) hand, the City-Scale [13] dataset contains only 180 satel-
| challengesinmodelgeneralizationcapabilities. |     |     |     |     |     | Toaddress |     |     |     |     |     |     |     |     |
| -------------------------------------------- | --- | --- | --- | --- | --- | --------- | --- | --- | --- | --- | --- | --- | --- | --- |
liteimagesof20citiesintheUnitedStates,withanimage
these limitations, we collect a new road graph extraction size of 2048 × 2048. While this dataset offers a broader
dataset, Global-Scale, which is ∼ 20× larger than exist- coverageareathanSpaceNet,itstillpredominantlyfocuses
| ing public | datasets. | Global-Scale |     | encompasses |     | all | conti- |          |              |     |      |                |     |           |
| ---------- | --------- | ------------ | --- | ----------- | --- | --- | ------ | -------- | ------------ | --- | ---- | -------------- | --- | --------- |
|            |           |              |     |             |     |     |        | on urban | environments | and | does | not adequately |     | represent |
nentsexceptAntarcticaandincludesroadsfromurban,ru- non-urban scenes, resulting in an overall insufficient data
| ral, mountainous, |            | and | other | complex       | environments. |           | Addi- |                  |               |              |               |              |          |         |
| ----------------- | ---------- | --- | ----- | ------------- | ------------- | --------- | ----- | ---------------- | ------------- | ------------ | ------------- | ------------ | -------- | ------- |
|                   |            |     |       |               |               |           |       | volume.          | Consequently, | current      | graph-labeled |              | datasets | fall    |
| tionally,         | to provide | a   | more  | comprehensive |               | benchmark | for   |                  |               |              |               |              |          |         |
|                   |            |     |       |               |               |           |       | short of meeting |               | modern model |               | requirements | [17,     | 44] for |
algorithm evaluation, we design both in-domain and out- large-scaleanddiversedatacoverage.
| of-domain | testing | sets | within | Global-Scale, |     | aiming | to ac- |     |     |     |     |     |     |     |
| --------- | ------- | ---- | ------ | ------------- | --- | ------ | ------ | --- | --- | --- | --- | --- | --- | --- |
countforthedomaindifferencespresentinglobalroadnet- https://spacenet.ai/challenges/
2

Table1.Summaryofpubliclyavailableroadextractiondatasets.Greyrowsindicatedatasetsthatdonotcontaingraphlabels.U,R,andM
denoteurban,rural,andmountainousareas,respectively.
|         |     |            |     |      |       |     | TestID | TestOOD |     |        |     |            |      |
| ------- | --- | ---------- | --- | ---- | ----- | --- | ------ | ------- | --- | ------ | --- | ---------- | ---- |
| Dataset |     | GraphLabel |     | Size | Train | Val |        |         | GSD | Region |     | RegionType | Time |
Massachusetts[31] ✗ 1,5002 1,108 14 49 ✗ 1.0 Massachusetts U,R 2013
|              |     |     | ✗   | 1,0242 | 6,226 |     |       | ✗   |     |                          |     |     |          |
| ------------ | --- | --- | --- | ------ | ----- | --- | ----- | --- | --- | ------------------------ | --- | --- | -------- |
| DeepGlobe[8] |     |     |     |        |       | 243 | 1,101 |     | 0.5 | Thailand,Indonesia,India |     |     | U,R 2013 |
SpaceNet[40] ✓ 4002 2,167 ✗ 567 ✗ 0.3 Paris,LasVegas,Shanghai U 2018
|                |     |     | ✓   | 2,0482 |     |     |      | ✗   |     |                 |     |     |        |
| -------------- | --- | --- | --- | ------ | --- | --- | ---- | --- | --- | --------------- | --- | --- | ------ |
| City-Scale[13] |     |     |     |        | 144 |     | 9 27 |     | 1.0 | 20cityintheU.S. |     |     | U 2020 |
Global-Scale ✓ 2,0482 2,375 339 624 130 1.0 Global U,R,M 2024
2.2.RoadGraphExtraction Notably,SAM-Road[15]firstextractssegmentationmasks,
andthenuseskeypointlocationinformation(fromsegmen-
| The existing | road | graph | extraction |     | methods | based | on  |                                                  |     |     |     |     |       |
| ------------ | ---- | ----- | ---------- | --- | ------- | ----- | --- | ------------------------------------------------ | --- | --- | --- | --- | ----- |
|              |      |       |            |     |         |       |     | tationmasks)todirectlypredictglobalconnectivity. |     |     |     |     | While |
satellite images can be divided into two categories: SAM-Roadreducesthenumberofpost-processingsteps,its
| segmentation-based |     | method | with | post-processing |     | and | end- |            |     |                |        |          |                 |
| ------------------ | --- | ------ | ---- | --------------- | --- | --- | ---- | ---------- | --- | -------------- | ------ | -------- | --------------- |
|                    |     |        |      |                 |     |     |      | dependence |     | on node labels | during | training | leads to a mis- |
to-endgraph-basedmethod. matchbetweenthetrainingandinferencephases.
| The segmentation-based |               |     | method     |     | [1, 5, 10, | 23,       | 26, 51] |     |     |     |     |     |     |
| ---------------------- | ------------- | --- | ---------- | --- | ---------- | --------- | ------- | --- | --- | --- | --- | --- | --- |
| leverage               | deep learning |     | technology |     | [11, 20]   | to obtain | the     |     |     |     |     |     |     |
3.Global-ScaleDataset
| segmentation | mask | of  | the road | from | images, | and | then ex- |     |     |     |     |     |     |
| ------------ | ---- | --- | -------- | ---- | ------- | --- | -------- | --- | --- | --- | --- | --- | --- |
tracts the road graph based on a series of complex post- A major challenge facing the road graph extraction task
| processing | methods | [7, | 22, | 50]. | For instance, |     | Gao et |     |          |                  |          |     |                |
| ---------- | ------- | --- | --- | ---- | ------------- | --- | ------ | --- | -------- | ---------------- | -------- | --- | -------------- |
|            |         |     |     |      |               |     |        | is  | the lack | of comprehensive | datasets |     | and benchmarks |
al. [10] proposed the Multi-Feature Pyramid Network [28,37].Table1showsthesurveyresultsofcurrentlyavail-
| (MFPN), | which | uses the | Feature | Pyramid | Network |     | (FPN) |      |                 |           |           |         |             |
| ------- | ----- | -------- | ------- | ------- | ------- | --- | ----- | ---- | --------------- | --------- | --------- | ------- | ----------- |
|         |       |          |         |         |         |     |       | able | road extraction | datasets, | revealing | several | key issues. |
[25]tocapturemulti-scalesemanticfeaturesandweighted First, theexisting graph-labeled datasets aresmall in scale
balancedlossfunction,improvingroadextractionaccuracy. andmainlyfocusonurbanareas.Incontrast,segmentation-
| Incontrast, | Lietal. | [23]developedaCNN-based[18,24] |     |     |     |     |     |         |          |         |             |          |                |
| ----------- | ------- | ------------------------------ | --- | --- | --- | --- | --- | ------- | -------- | ------- | ----------- | -------- | -------------- |
|             |         |                                |     |     |     |     |     | labeled | datasets | are not | only larger | in scale | but also cover |
frameworkthatextractsroadfeaturesfromsmallSynthetic multipletypessuchascitiesandfarmland. Second,current
Aperture Radar (SAR) image patches [33], identifies can- roadextractiondatasetsarelimitedtothecityscale,lacking
| didate road | regions, | groups, |     | them | analyzes | road | network |                                    |     |     |     |                     |     |
| ----------- | -------- | ------- | --- | ---- | -------- | ---- | ------- | ---------------------------------- | --- | --- | --- | ------------------- | --- |
|             |          |         |     |      |          |      |         | aglobalscaleroadextractiondataset. |     |     |     | Finally,althoughthe |     |
connectivitywithMarkovRandomField(MRF).Although training set of SpaceNet is large in scale, the size of each
segmentation-basedmethodscangenerateroadgraph,their
imageissmall(400×400),resultinginalimitedcoverage
performanceintermsoftopologicalconnectivityislimited area,androadsareusuallyelongatedandconnectivity[52],
[43]. Additionally,whiletheyrelyonpost-processingopti- such a size may only include some shorter roads, result-
mizations,theresultsremainconstrained.
|     |     |     |     |     |     |     |     | inginlimitedcontextualinformation. |     |     |     | AlthoughCity-Scale |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ---------------------------------- | --- | --- | --- | ------------------ | --- |
providesalargerimagesize(2,048×2,048),whichsolves
| The graph-based |     | methods |     | are gradually | emerging |     | to get |     |     |     |     |     |     |
| --------------- | --- | ------- | --- | ------------- | -------- | --- | ------ | --- | --- | --- | --- | --- | --- |
a better graph of the road topology in an end-to-end fash- thecoverageproblem,ithasasmallnumberofimages,es-
ion. It can be further divided into iteration-based method pecially the test set has only 27 images, which makes the
modelevaluationsusceptibletosignificantimpactfromthe
| [2,45,46]andglobal-basedmethod[13,15]. |     |     |     |     |     | Theiteration- |     |     |     |     |     |     |     |
| -------------------------------------- | --- | --- | --- | --- | --- | ------------- | --- | --- | --- | --- | --- | --- | --- |
basedmethodsbuildthecompleteroadstructurebypredict- performanceofasingleimage.
ingroadnodes(vertices)stepbystep.TheearlyRoadTracer OurGlobal-Scaledatasetisacomprehensiveroadgraph
[2] model started from the initial node and gradually built resourcecoveringallcontinentsexceptAntarctica,designed
a road graph with fixed angles and step sizes. RNGDet toaddressthegapsinexistinggraph-labeleddatasets. Fig-
[45] and RNGDet++ [46] combine CNN and Transformer ure 1 illustrates the collection methodology of the Global-
[39, 41, 48] to extract features and iteratively predict ver- Scaledataset. Specifically,Wemanuallyselectedthelongi-
tices,whichsignificantlyimprovestheabilitytocapturethe tudeandlatitudeofvarioustypesofroads,includingurban,
globalstructureoftheroad.However,duetopoint-by-point rural, and mountainous, using Google Earth [27, 34]. We
iteration,thistypeofmethodistime-consuming,anderrors thengatheredhigh-qualitysatelliteimagesfromtheGoogle
tend to accumulate as points are iterated. In contrast, the StaticMapAPI[38]basedontheselectedlatitudeandlon-
global-basedmethod[13,15]candirectlygenerateacom- gitude information, as well as from the commonly used
pleteroadgraphwithsignificantlyimprovedefficiency. For open-sourceOpenStreetMap[12]databasetoobtaincorre-
example, Sat2Graph [13] trains the model through graph spondingroadgraphdataasgroundtruth. Eachimagehas
codingtensors,directlypredictsthegraphtensorcodingof aspatialresolutionof1m/pixel,followingthestandardsset
roads,andgeneratesvectorgraphsthroughpost-processing. by [13]. However, the annotation completeness of Open-
3

𝓛
𝓶𝓪𝓼𝓴
Mask
Satellite image SAM-Encoder Feature map Decoder Road mask Generator
Mask label
k
|     |     |     |     | sa  |     |     | NMS |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
m
 d
|     |     |     |     | n   |     |     |     |     |     | Ground truth |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ------------ | --- | --- |
e
tx
E
|     |     | Connectivity |     |     |             |     |     |     |     |     | Node      |     |
| --- | --- | ------------ | --- | --- | ----------- | --- | --- | --- | --- | --- | --------- | --- |
|     |     | Classifier   | …   |     | Extend-line |     |     |     |     |     | Generator |     |
.ta
|     |     |     |     | e f e |     |     |     |     | R o a d   li n e |     |     |     |
| --- | --- | --- | --- | ----- | --- | --- | --- | --- | ---------------- | --- | --- | --- |
Road graph
|     |     |     |     | d   |     |     |                  |     | So u r c e   n ode | Sampled nodes |     |     |
| --- | --- | --- | --- | --- | --- | --- | ---------------- | --- | ------------------ | ------------- | --- | --- |
|     |     |     |     | o N |     |     | Re-sampled nodes |     | Target node        |               |     |     |
New target node
|     |     |     |     |     | Node-centered patch |     |     | Node-guided resampling |     |     |     |     |
| --- | --- | --- | --- | --- | ------------------- | --- | --- | ---------------------- | --- | --- | --- | --- |
𝓛
𝒕𝒐𝒑𝒐
Figure2. OverviewofourproposedSAM-Road++. Theredlineindicatestrainingonlyandthebluelineindicatesinferenceonly. The
satelliteimageisfedintoSAM[19]EncoderandDecodertogetthefeaturemapandroadmask.Duringtraining,theproposednode-guided
resamplingusesthegroundtruthandroadmasktogetthere-samplednodes.Intheinferencestage,thenodesareobtainedusingonlyroad
masksthroughNon-MaximumSuppression(NMS).Finally, theconnectivityclassifierdetermineswhetheraroadexistsbetweennodes
basedonthenodefeaturesandtheextendedlinebetweenthenodes. BothlossfunctionsL mask andL topo arebinarycross-entropyloss,
whereL andL areusedtosupervisetheroadsegmentationandthetopologicalconnectivityoftheroad,respectively.
| mask | topo |     |     |     |     |     |     |     |     |     |     |     |
| ---- | ---- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
StreetMap can be affected by variations in population size tion model [16, 36] into the field of road graph extraction.
andeconomicdisparitiesacrossregions[14]. Toensurethe AssumethattheroadgraphisG = (V,E),whereV isthe
annotation completeness of the Global-Scale dataset, we set of road nodes of the road graph (i.e. vertices) and E
(i.e.
conducted a thorough second screening of the annotations is the set of road lines edges). The training phase of
aftertheinitialdatacollectiontoconfirmtheintegrityofour SAM-Road consists of two stages. In the first stage, an
roadgraphlabels. RGB satellite image is fed into the SAM encoder to ex-
Finally,theGlobal-Scaledatasetcontains3,468satellite tractimagefeatureembeddings. Thedecoderthenpredicts
images,eachwithasizeof2048×2048,providingexten- per-pixel probabilities for the existence of road lines and
nodesintheformofmasks.Inthesecondstage,SAM-Road
sivespatialcoverageandavarietyofroadtypes.Thedataset
isdividedintotraining(2,375images),validation(339im- randomly samples nodes (position information) and corre-
|            |           |               |     |          |             |     | sponding edges | (road | information) | from the | ground | truth. |
| ---------- | --------- | ------------- | --- | -------- | ----------- | --- | -------------- | ----- | ------------ | -------- | ------ | ------ |
| ages), and | test sets | (624 images). |     | Notably, | to evaluate | the |                |       |              |          |        |        |
model’s inference capability in unseen cities, we addition- Usingthesenodepairs,SAM-Roademploystheimageem-
allycollected130imagesfromHongKong,Shenzhen,and beddingsofthenodepairsobtainedinthepreviousstageas
inputtotrainaroadclassifiertogettheprobabilityofaroad
Lucerne,whicharenotincludedinthetrainingset,serving
asanout-of-domaintestset. Thisdesignensuresthegener- existingbetweentwonodes.
alizationabilityofthemodelindifferentgeographicalenvi- Duringtheinferencephase,groundtruthisnotavailable,
ronments can be evaluated. In summary, the Global-Scale therefore, SAM-Road selects road nodes from the masks
| dataset not | only provides | abundant |     | training | resources | but |     |     |     |     |     |     |
| ----------- | ------------- | -------- | --- | -------- | --------- | --- | --- | --- | --- | --- | --- | --- |
predictedinthefirststageasinputsfortheclassifierofthe
also establishes a robust benchmark for future road graph secondstage.Asfortheselectionofnodes,SAM-Roadem-
| extraction         | research, | allowing    | researchers | to          | more compre- |         |                     |     |             |       |          |       |
| ------------------ | --------- | ----------- | ----------- | ----------- | ------------ | ------- | ------------------- | --- | ----------- | ----- | -------- | ----- |
|                    |           |             |             |             |              |         | ploys a Non-Maximum |     | Suppression | (NMS) | strategy | [15], |
| hensively evaluate |           | and compare | the         | performance | of           | differ- |                     |     |             |       |          |       |
whichprioritizesnodeswithhigherpredictionprobabilities
entroadgraphextractionmodels. whilefilteringoutsurroundingnodes.
However,asignificantissuearisesfromthefactthatthe
4.Methodology
|     |     |     |     |     |     |     | classifier trained | on  | ground truth | nodes does | not | perform |
| --- | --- | --- | --- | --- | --- | --- | ------------------ | --- | ------------ | ---------- | --- | ------- |
effectivelyonthenodesobtainedfromsegmentationmasks
4.1.Preliminary
|     |     |     |     |     |     |     | during the inference |     | process, | which indicates | a   | mismatch |
| --- | --- | --- | --- | --- | --- | --- | -------------------- | --- | -------- | --------------- | --- | -------- |
SAM-Road [15] is the first global-based end-to-end road between training and inference. Consequently, ensuring
graph extraction method and the first to bring the founda- that the classifier exhibits consistent behavior during both
4

|     |     |     |     |     |     | within a     | distance   | R, along | with  | the connectivity |        | informa-     |
| --- | --- | --- | --- | --- | --- | ------------ | ---------- | -------- | ----- | ---------------- | ------ | ------------ |
|     |     |     |     |     |     | tion between | these      | target   | nodes | and the          | source | node. This   |
|     |     |     |     |     |     | process      | yields the | sampled  | nodes | (both            | source | and target). |
Additionally,toensurediversityamongthesamplednodes,
R we leverage the inherent degree attributes of the graph for
Road line sourcenodeselection,specificallyfavoringnodeswithrarer
|     |     |     | Source node |     |     | degreeattributes,whichareeasiertosample. |     |     |     |     |     |     |
| --- | --- | --- | ----------- | --- | --- | ---------------------------------------- | --- | --- | --- | --- | --- | --- |
|     | R   |     |             |     | R   |                                          |     |     |     |     |     |     |
Target node
Road line Road line Forthesamplednodes,toalignmorecloselywiththein-
|     | S o u rc e   n o d e |     | New target node |     | S o u rc e   n o d e |     |     |     |     |     |     |     |
| --- | -------------------- | --- | --------------- | --- | -------------------- | --- | --- | --- | --- | --- | --- | --- |
T a rg e t  n o d e T a rg e t  n o d e ferenceprocess, weleavethesourcenodesunchangedand
| Sampled nodes |     |     |     | Re-sampled nodes |     |     |     |     |     |     |     |     |
| ------------- | --- | --- | --- | ---------------- | --- | --- | --- | --- | --- | --- | --- | --- |
Node-guided resampling usearadiusofr toselectanewtargetnodewiththehigh-
Figure3. Illustratingtheprocessofnode-guidedresampling. The estprobability,centeredaroundeachsourcenode. Wethen
sampled nodes are obtained by sampling from the ground truth, save the coordinate information of this new target node in
and R represents the maximum distance threshold between the place of the old one. This results in the creation of re-
source node and target node during the sampling process. Then sampled nodes. The re-sampled nodes not only retain the
foreachtargetnode,ournode-guidedresamplingstrategywillfind source nodes of the ground truth and the connectivity be-
themaximumprobabilitypointofthemaskaroundthetargetnode
|     |     |     |     |     |     | tween the | nodes, | but the | position | information |     | of the new |
| --- | --- | --- | --- | --- | --- | --------- | ------ | ------- | -------- | ----------- | --- | ---------- |
andsaveitasthenewtargetnode.rrepresentsthemaximumdis-
targetnodesalsomatchesthenodeselectionstrategyinthe
tancethresholdbetweenthetargetnodeandnewtargetnode.
|     |     |     |     |     |     | inference.        | Atthesametime, |                                     | byusingthemaximumprob- |                   |     |            |
| --- | --- | --- | --- | --- | --- | ----------------- | -------------- | ----------------------------------- | ---------------------- | ----------------- | --- | ---------- |
|     |     |     |     |     |     | ability of        | the predicted  |                                     | road mask              | to pick           | the | new target |
|     |     |     |     |     |     | nodes, it         | takes          | full advantage                      |                        | of the experience |     | gained in  |
|     |     |     |     |     |     | thepreviousstage. |                | Thisstrategycompensatesfortheshort- |                        |                   |     |            |
comingsinthetrainingprocessandeffectivelyimprovesthe
consistencyofthemodelduringtrainingandinference.
4.3.“Extended-line”strategy
(b)
|     |     |     |     |     |     | Both in | the inference | and | training | process, | once | the loca- |
| --- | --- | --- | --- | --- | --- | ------- | ------------- | --- | -------- | -------- | ---- | --------- |
tionsofthenodesaredetermined,theroadclassifierneeds
tomakeroadpredictionbetweenthesourcenodeandtarget
|     |     |     |     |     |     | node. However, |               | sincethemodelcanonlyextractinforma- |       |              |            |             |
| --- | --- | --- | --- | --- | --- | -------------- | ------------- | ----------------------------------- | ----- | ------------ | ---------- | ----------- |
|     |     |     |     |     |     | tion from      | a single      | overhead                            | view  | in satellite |            | images, the |
|     |     |     |     |     |     | determination  | of            | connectivity                        |       | between      | road nodes | is sus-     |
|     |     | (a) |     |     | (c) |                |               |                                     |       |              |            |             |
|     |     |     |     |     |     | ceptible       | to occlusion, | as                                  | shown | in Figure    | 4. To      | tackle this |
Figure4.Illustrationofocclusionchallengeinroadnodesconnec- issue,weproposethe“extended-line”strategy.
tivityfromsatelliteimages.(a)istherawsatelliteimage,(b)isthe
Forapairofre-samplednodesrequiredforconnectivity
| prediction | of SAM-Road | [15], | and (c) | is the prediction | with the |     |     |     |     |     |     |     |
| ---------- | ----------- | ----- | ------- | ----------------- | -------- | --- | --- | --- | --- | --- | --- | --- |
discrimination,weusetheircoordinatesintheimagetoex-
“extended-line”strategy.
tracttheirnode-centeredpatchinfeaturemapobtainedfrom
|     |     |     |     |     |     | SAM-Encoder,calledsourceandtargetfeatures. |     |     |     |     |     | Consider- |
| --- | --- | --- | --- | --- | --- | ------------------------------------------ | --- | --- | --- | --- | --- | --------- |
ingtheextensibilityoftheroadandtheinfluenceoffactors
| training | and inference | is critical | for | road graph | extraction. |     |     |     |     |     |     |     |
| -------- | ------------- | ----------- | --- | ---------- | ----------- | --- | --- | --- | --- | --- | --- | --- |
To address this challenge, we propose a novel “node sam- suchastreeshadowsonroadjudgment,webelievethatthe
pling”strategy. informationbetweenthetwonodesandtheinformationon
theirextensionscanalsoeffectivelyassistthemodelinpre-
4.2.Node-guidedresampling
|     |     |     |     |     |     | dictingtheexistenceoftheroad. |     |     |     | Therefore, | weuniformly |     |
| --- | --- | --- | --- | --- | --- | ----------------------------- | --- | --- | --- | ---------- | ----------- | --- |
sampledthemaskvaluesatbothendsoftherespectiveex-
| Our goal | is to align | the nodes | provided | to the | classifier |     |     |     |     |     |     |     |
| -------- | ----------- | --------- | -------- | ------ | ---------- | --- | --- | --- | --- | --- | --- | --- |
tensionsntimesbyusingtheroadmaskspreviouslygener-
| during | training more | closely | with those | used in | inference. |         |            |     |           |         |           |        |
| ------ | ------------- | ------- | ---------- | ------- | ---------- | ------- | ---------- | --- | --------- | ------- | --------- | ------ |
|        |               |         |            |         |            | ated by | the model. | In  | addition, | we also | uniformly | sample |
However,ifwedirectlyadopttheinferenceprocessfornode
mtimesonthelinebetweenthesetwonodes.
| selection—specifically |     | using | the NMS | strategy—the | con- |     |     |     |     |     |     |     |
| ---------------------- | --- | ----- | ------- | ------------ | ---- | --- | --- | --- | --- | --- | --- | --- |
nectivityinformationnecessarytosupervisethelearningof
4.4.Inference
theclassifierbecomesunavailable.Toaddressthisissue,we
propose a compromise strategy called node-guided resam- In the inference process, we input the satellite images into
pling,asillustratedinFigure3. theSAMencoderanddecoderandobtainthepredictedseg-
First, we sample N nodes (referred to as source nodes) mentmasks,includingroadmaskandkeypointmask.First,
from the ground truth through a node generator. For each we use NMS to deal with the road mask in three steps: 1)
source node, we then identify and save all target nodes we set all pixel values in the mask less than the threshold
5

Table2.ComparisonofSAM-Road++withothermethodsoncurrentlypubliclyavailabledatasets,Thebestresultsarehighlightedinbold
font, andthesecondresultisunderlined. *denotespre-trainingontheGlobal-Scaledataset. Forallthemetrics, largervaluesindicate
betterperformance.
City-Scale SpaceNet
F1 Precision Recall APLS F1 Precision Recall APLS
Sat2Graph[13] 76.26 80.70 72.28 63.14 80.97 85.93 76.55 64.43
RNGDet[45] 76.87 85.97 69.87 65.75 81.13 90.91 73.25 65.61
RNGDet++[46] 78.44 85.65 72.58 67.76 82.51 91.34 75.24 67.73
SAM-Road[15] 77.23 90.47 67.69 68.37 80.52 93.03 70.97 71.64
Ours 80.01 88.39 73.39 68.34 81.57 93.68 72.23 73.44
Ours* 80.66 89.08 74.07 69.55 82.07 93.97 72.84 74.35
t to 0, and 2) find the coordinates (x , y ) of the largest TheTOPOcomparesthesimilarityofreachablesubgraphs
1 i i
probabilityinthemaskandsaveittothesetV ,thensetall ofthesameverticesinthepredictedgraphandgroundtruth
1
pixel values around (x , y ) within the threshold radius r intermsofprecision, recallandF1. TheAPLSmetric, on
i i 1
to 0. Next, 3) repeat the second step until all the non-zero theotherhand,focusesontheaccuracyoftheshortestpath
pixel points have been traversed. For the key point mask, betweentwolocationsintheroadgraph.Thismetricisvery
weusethethresholdl andthethresholdradiusr torepeat sensitive to path quality and is well suited to assessing the
2 2
theabovethreestepstoobtainthesetV . Finally,wemerge accuracyofroadconnectivity.
2
the obtained location sets V and V together to obtain the
1 2
finalroadnodesinformation,whichcanbeusedforthesub- 5.3.Implementation
sequentconnectivityprediction. Itisworthmentioningthat
For both the City-Scale and Global-Scale datasets, we ex-
the use of thresholds l , l and radius r , r ensures that
1 2 1 2 tracted 512 × 512 pixel image patches from the satellite
we get the node with the largest probability within a cer-
images with the batch size set to 16, and set the number
tainrange,whichalsocorrespondswelltothenode-guided
of sampled source nodes N for each patch to 512. For
resamplingthatweadoptinthetrainingphase.
SpaceNet,thepatchsizeissetto256×256,thebatchsize
In the connectivity discrimination stage, each node is
to64,andthenumberofsourcenodesN perpatchissetto
consideredasasourcenode,andthenodesinitssurround-
128. Inthesamplingphase,Rissetto16pixels,andsetr
ing range as target nodes. For each pair of source and tar-
to8pixelsinthesamplingphaseforalldatasets. Intheim-
get nodes, we use the “extended-line” strategy to extract
plementationof“extended-line”,sincetheresolutionofall
information input to the connectivity classifier to predict
thedatasetsis1m/pixel,wesetthelengthontheendsofthe
the probability of whether a road exists between the pair
respectiveextendedlinesto8pixelsandthensetthewidth
of nodes. Since each node will be a source node and the
ofthelineto3pixelstosimulatearoad, aswellassetting
sameroadsmaybepredictedmultipletimes,weaverageall
thenumberofsamplesnto15andmto20.Intheinference
theobtainedroadscorestogetthefinalroadgraph.
phase,wesetradiusr to16andradiusr to8. Thebinary
1 2
classificationthresholdst ,t ,andt arethethresholdsthat
5.Experiments 1 2 3
yieldthehighestF scoreonthevalidationset.
1
5.1.Datasets We use the Adam optimizer with a basic learning rate
of 0.001. For SpaceNet and City-Scale datasets, we train
In this paper, we provide a comprehensive evaluation of
SAM-Road++untilthevalidationmetricsstabilize,follow-
three datasets, City-Scale [13], SpaceNet [40] and our
ing[15].ForGlobal-Scale,SAM-Road++istrainedfor150
Global-Scale. Table1showsthebasicinformationofthese
epochs. Allexperimentsareconductedonone4090GPU.
three datasets, which includes important details such as
dataset size and spatial resolution. Additionally, to ensure
5.4.ComparativeResults
the fairness of experiments, for SpaceNet, we refer to the
pre-processingmethodofpreviousworks[13,15]. Specif- WeevaluatetheSAM-Road++modelontheCity-Scaleand
ically,weadjustthespatialresolutionofsatelliteimagesin SpaceNetdatasetsandquantitativelycompareditwithother
theSpaceNetdatasetto1m/pixel. methods, as shown in Table 2. We compare four typical
methods,includingtwoiteration-basedmethods(RNGDet,
5.2.Metrics
RNGDet++) and two global-based methods (Sat2Graph,
Toevaluatetheperformanceofmodels,weusetwometrics: SAM-Road). The experimental results show that our
TOPO[4]andAveragePathLengthSimilarity(APLS)[40]. methodoutperformsexistingSOTAmethodsinF1metrics
6

|     | Ground truth | RNGDet++ |     | SAM-Road | Ours |
| --- | ------------ | -------- | --- | -------- | ---- |
(a)
(b)
(c)
Figure5. ThevisualizedroadnetworkgraphpredictionsofSAM-Road++andtwobaselinemethods. Betterzoom-inandviewincolor.
Overall,thepredictionaccuracyofSAM-Road++ishigher. Inthecrossroadsregions(aandb),SAM-Road++successfullypredictedthe
complexityofmultipleroundaboutsandoverpasses,andinpredictingthetree-shadedregionc,SAM-Road++’spredictionresultisalso
morecompletecomparedtotheothertwobaselines.
Table3.Comparisonwithdifferentmethodsonglobal-scale.OurmethodsignificantlyoutperformstheothermethodsontheAPLSmetrics
onbothin-domainandout-of-domaintestsets,andalthoughwedonotachievesotaontheprecisionmetric,itperformsfarbetteronthe
morecomprehensiveF1metriconbothin-domainandout-of-domaintestsets.
|     |     | Global-Scale(In-Domain) |             | Global-Scale(Out-of-Domain) |             |
| --- | --- | ----------------------- | ----------- | --------------------------- | ----------- |
|     |     | F1 Precision            | Recall APLS | F1 Precision                | Recall APLS |
Sat2Graph[13] 35.53 90.15 22.13 26.77 30.64 84.73 19.75 22.49
|     | RNGDet[45]   | 52.59 79.89 | 40.72 49.43 | 42.62 68.79 | 32.60 36.33 |
| --- | ------------ | ----------- | ----------- | ----------- | ----------- |
|     | RNGDet++[46] | 55.04 79.02 | 45.23 52.72 | 47.34 70.22 | 35.71 38.08 |
|     | SAM-Road[15] | 59.80 91.93 | 45.64 59.08 | 46.64 84.54 | 33.81 40.51 |
|     | Ours         | 62.33 88.95 | 49.27 62.19 | 48.34 82.21 | 36.04 43.17 |
forCity-ScaleandSpaceNetdatasets,demonstratingthead- truth,albeitwithreducedscore.
| vantages in overall | topology extraction. | However, | on the |     |     |
| ------------------- | -------------------- | -------- | ------ | --- | --- |
FortheAPLSmetrics,theperformanceontheSpaceNet
City-Scaledataset, althoughourrecallishigherthanother is better than other methods, which indicates that our pro-
methods, the precision is slightly lower than SAM-Road. posed“extended-line”strategyhelpsthemodeltoinferroad
Thisismainlyduetothefactthatintheinference,aseriesof lengths closer to the ground truth. Meanwhile, the APLS
nodepairsobtainedthroughNMSdonotexactlymatchthe of our method on the City-Scale dataset is comparable to
ground truth. The node-guided resampling strategy makes that of SAM-Road. We note that the City-Scale test set
the node pairs used in the training phase closer to the in- contains so few satellite images (only 27 images) that the
ference. As a result, our model is able to identify roads per-image prediction has a significant impact on the final
between the node pairs that may deviate from the ground APLS metric, which results in the APLS metric being un-
7

Ground-truth RNGDet++ SAM-Road Ours Table 4. Ablation results for “extended line” strategy and node-
guidedresampling.
(a)
|     |     |     |     |     |     |     | “extended-line”       |     | node-guidedresampling |                               |     | APLS  | F1    |
| --- | --- | --- | --- | --- | --- | --- | --------------------- | --- | --------------------- | ----------------------------- | --- | ----- | ----- |
|     |     |     |     |     |     |     |                       | ✗   |                       | ✗                             |     |       |       |
|     |     |     |     |     |     |     |                       |     |                       |                               |     | 71.64 | 80.52 |
|     |     |     |     |     |     |     |                       | ✗   |                       | ✓                             |     |       |       |
|     |     |     |     |     |     |     |                       |     |                       |                               |     | 71.90 | 81.77 |
| (b) |     |     |     |     |     |     |                       | ✓   |                       | ✗                             |     | 73.22 | 80.89 |
|     |     |     |     |     |     |     |                       | ✓   |                       | ✓                             |     | 73.44 | 81.57 |
|     |     |     |     |     |     |     | widerangeofscenarios. |     |                       | Althoughtheoverallperformance |     |       |       |
(c)
|     |     |     |     |     |     |     | on the | out-of-domain  |            | test set | is lower      | than that | on the in-  |
| --- | --- | --- | --- | --- | --- | --- | ------ | -------------- | ---------- | -------- | ------------- | --------- | ----------- |
|     |     |     |     |     |     |     | domain | test set,      | our method | still    | significantly |           | outperforms |
|     |     |     |     |     |     |     | the    | other methods, | suggesting |          | that our      | method    | is more ro- |
Figure 6. Visualisation of the different methods on the out-of- busttounseenregionaldatathantheothermethods,andis
domaintestset. Intheruralroadregionwithfarmlandascontext moresuitableforreal-worldapplications.
|     |     |     |     |     |     |     | Finally, | by  | comparing | the | results | in Table | 2 and Ta- |
| --- | --- | --- | --- | --- | --- | --- | -------- | --- | --------- | --- | ------- | -------- | --------- |
((a)and(b)),ourmethodsuccessfullyavoidsroaddisconnection.
Intheroadregion(c)withtheshadowofatallbuilding,ourpro- ble 3, it can be seen that all five models do not perform
posed“extended-line”strategyaccuratelypredictstheconnectiv- as well on Global-Scale as they did on City-Scale and
ityoftheshadedportions.
SpaceNet,whichfurtherdemonstratesthatGlobal-Scaleis
amorechallengingdatasettobetterevaluatethegeneraliza-
reliable. In addition, to further validate the usefulness of tionabilityofmodelsincomplexscenarios.
| our proposed | Global-Scale |     | dataset, | we  | pre-trained | SAM- |     |     |     |     |     |     |     |
| ------------ | ------------ | --- | -------- | --- | ----------- | ---- | --- | --- | --- | --- | --- | --- | --- |
Road++onGlobal-Scaleandfine-tuneditontheCity-Scale 5.6.AblationStudies
| andSpaceNetdatasets. |     |     | Theexperimentalresultsshowthat |     |     |     |     |     |     |     |     |     |     |
| -------------------- | --- | --- | ------------------------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
Inthissection,weconductablationstudiestoverifythera-
| the introduction |     | of the | Global-Scale |     | dataset significantly |     |     |     |     |     |     |     |     |
| ---------------- | --- | ------ | ------------ | --- | --------------------- | --- | --- | --- | --- | --- | --- | --- | --- |
tionalityofthedesignofSAM-Road++,includingthenode-
| improves | the model’s |     | performance | in  | terms of | APLS and |        |            |     |                 |     |           |          |
| -------- | ----------- | --- | ----------- | --- | -------- | -------- | ------ | ---------- | --- | --------------- | --- | --------- | -------- |
|          |             |     |             |     |          |          | guided | resampling | and | “extended-line” |     | strategy, | as shown |
TOPOmetricsonbothdatasets.
|     |     |     |     |     |     |     | in Table | 4. First, | we  | completely | remove | the | node-guided |
| --- | --- | --- | --- | --- | --- | --- | -------- | --------- | --- | ---------- | ------ | --- | ----------- |
resamplingstrategyfromthetrainingandobserveasignifi-
5.5.BenchmarkingonGlobal-Scale
cantdecreaseinthemodel’sperformanceontheF1metric.
Figure5andFigure6showthequalitativeresultsofSAM-
Thissuggeststhatthenode-guidedresamplingindeedsimu-
Road++onthein-domainandout-of-domaintestsetsofthe
latestheinferenceprocessintraining,enablingthemodelto
| global-scaledataset, |     | respectively. |     | Ascanbeseenfromthe |     |     |     |     |     |     |     |     |     |
| -------------------- | --- | ------------- | --- | ------------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- |
predictbettertopologies.Next,weeliminatethe”extended-
| circled areas | in  | regions | (a) and | (b) in | Figure 5, | when fac- |     |     |     |     |     |     |     |
| ------------- | --- | ------- | ------- | ------ | --------- | --------- | --- | --- | --- | --- | --- | --- | --- |
line”strategyandfindthattheAPLSdecreases,suggesting
| ing complex | intersections  |     | such | as overpasses | and       | multiple |      |              |             |       |     |       |              |
| ----------- | -------------- | --- | ---- | ------------- | --------- | -------- | ---- | ------------ | ----------- | ----- | --- | ----- | ------------ |
|             |                |     |      |               |           |          | that | our strategy | effectively | helps | the | model | predict road |
| roundabouts | intersections, |     | the  | key nodes     | predicted | by the   |      |              |             |       |     |       |              |
lengthsthatareclosertothegroundtruth.
| models are | not             | very accurately |            | localized | on the        | road, but |     |     |     |     |     |     |     |
| ---------- | --------------- | --------------- | ---------- | --------- | ------------- | --------- | --- | --- | --- | --- | --- | --- | --- |
| owing to   | the node-guided |                 | resampling |           | strategy used | in the    |     |     |     |     |     |     |     |
6.Conclusion
| training | phase, | SAM-Road++ |     | is able | to accurately | deter- |     |     |     |     |     |     |     |
| -------- | ------ | ---------- | --- | ------- | ------------- | ------ | --- | --- | --- | --- | --- | --- | --- |
mine the connectivity of road nodes in this complex scene In this paper, we present a large-scale dataset, Global-
duringtheinferencephase. TheareascircledinFigure5(c) Scale, and a novel method, SAM-Road++, for road graph
and Figure 6(c) are obscured by the shadows of buildings extraction. The Global-Scale encompasses six continents
and vegetation on the side of the road, which is an inher- and has been meticulously curated to include a diverse ar-
ent challenge to the road graph extraction task. Previous ray of scenes, such as urban, rural, and mountainous ar-
methodscannotdiscriminateundersuchconditions,andthe eas. SAM-Road++ effectively addresses the mismatch be-
“extendedline”strategyinSAM-Road++effectivelyavoids tweentrainingandinferenceinglobal-basedmethodswhile
roadbreaksbasedontheextendedpropertiesoftheroad. mitigating the occlusion challenges inherent in road graph
Forfurthercomparison,wetrainedthefivemodelsmen- extraction tasks. Extensive experiments demonstrate that
tioned in the previous section on the Global-Scale dataset, Global-Scale serves as a more comprehensive and chal-
which contains more comprehensive data, and validated lenging benchmark. In addition, SAM-Road++ achieves
them on both the in-domain test set and out-of-domain superior performance on both existing public datasets and
test set and the results are shown in Table 3. On the in- Global-Scale,withoutincurringsignificantinferencecosts.
domain test set, our method significantly outperforms pre- Lookingahead,weplantofurtherexpandtheGlobal-Scale
vious methods in both APLS and TOPO metrics, which dataset and endeavor to innovate the paradigm of the road
| indicates | that our | method | outperforms |     | other methods | in a | extractiontask. |     |     |     |     |     |     |
| --------- | -------- | ------ | ----------- | --- | ------------- | ---- | --------------- | --- | --- | --- | --- | --- | --- |
8

References generatedstreetmaps. IEEEPervasivecomputing,7(4):12–
|     |     |     |     |     |     |     | 18,2008. | 3   |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | -------- | --- | --- | --- | --- | --- | --- |
[1] Abolfazl Abdollahi, Biswajeet Pradhan, and Abdullah [13] Songtao He, Favyen Bastani, Satvat Jagwani, Mohammad
| Alamri. | Vnet:Anend-to-endfullyconvolutionalneuralnet- |     |     |     |     |     |           |                   |     |     |               |     |          |
| ------- | --------------------------------------------- | --- | --- | --- | --- | --- | --------- | ----------------- | --- | --- | ------------- | --- | -------- |
|         |                                               |     |     |     |     |     | Alizadeh, | HariBalakrishnan, |     |     | SanjayChawla, |     | MohamedM |
workforroadextractionfromhigh-resolutionremotesens-
|          |                                  |     |     |     |     |     | Elshrif,   | Samuel                                    | Madden, | and | Mohammad | Amin | Sadeghi. |
| -------- | -------------------------------- | --- | --- | --- | --- | --- | ---------- | ----------------------------------------- | ------- | --- | -------- | ---- | -------- |
| ingdata. | IeeeAccess,8:179424–179436,2020. |     |     |     |     | 3   |            |                                           |         |     |          |      |          |
|          |                                  |     |     |     |     |     | Sat2graph: | Roadgraphextractionthroughgraph-tensoren- |         |     |          |      |          |
[2] FavyenBastani,SongtaoHe,SofianeAbbar,MohammadAl- coding. In Computer Vision–ECCV 2020: 16th European
izadeh, Hari Balakrishnan, Sanjay Chawla, Sam Madden, Conference, Glasgow, UK, August 23–28, 2020, Proceed-
| and David     | DeWitt. | Roadtracer: |         | Automatic |             | extraction of |       |           |     |       |                  |       |          |
| ------------- | ------- | ----------- | ------- | --------- | ----------- | ------------- | ----- | --------- | --- | ----- | ---------------- | ----- | -------- |
|               |         |             |         |           |             |               | ings, | Part XXIV | 16, | pages | 51–67. Springer, | 2020. | 1, 2, 3, |
| road networks |         | from aerial | images. | In        | Proceedings | of the        |       |           |     |       |                  |       |          |
6,7
| IEEE | conference | on computer |     | vision | and pattern | recogni- |               |          |      |             |     |             |          |
| ---- | ---------- | ----------- | --- | ------ | ----------- | -------- | ------------- | -------- | ---- | ----------- | --- | ----------- | -------- |
|      |            |             |     |        |             |          | [14] Benjamin | Herfort, | Sven | Lautenbach, |     | Joa˜o Porto | de Albu- |
tion,pages4720–4728,2018. 1,3 querque,JenningsAnderson,andAlexanderZipf. Aspatio-
[3] AnilBatra,SuriyaSingh,GuanPang,SaikatBasu,CVJawa- temporal analysis investigating completeness and inequali-
har,andManoharPaluri.Improvedroadconnectivitybyjoint
|     |     |     |     |     |     |     | tiesofglobalurbanbuildingdatainopenstreetmap. |     |     |     |     |     | Nature |
| --- | --- | --- | --- | --- | --- | --- | --------------------------------------------- | --- | --- | --- | --- | --- | ------ |
learningoforientationandsegmentation. InProceedingsof Communications,14(1):3985,2023. 4
theIEEE/CVFConferenceonComputerVisionandPattern [15] CongruiHetang,HaoruXue,CindyLe,TianweiYue,Wen-
Recognition,pages10385–10393,2019. 2 pingWang,andYihuiHe. Segmentanythingmodelforroad
|           |          |           |           |     |           |           | networkgraphextraction. |     |     | InProceedingsoftheIEEE/CVF |     |     |     |
| --------- | -------- | --------- | --------- | --- | --------- | --------- | ----------------------- | --- | --- | -------------------------- | --- | --- | --- |
| [4] James | Biagioni | and Jakob | Eriksson. |     | Inferring | road maps |                         |     |     |                            |     |     |     |
fromglobalpositioningsystemtraces: Surveyandcompar- Conference on Computer Vision and Pattern Recognition,
ative evaluation. Transportation research record, 2291(1): pages2556–2566,2024. 1,2,3,4,5,6,7
61–71,2012. 6 [16] DanfengHong,BingZhang,XuyangLi,YuxuanLi,Chenyu
|               |                    |     |                |                 |         |             | Li, JingYao,   |     | NaotoYokoya, |     | HaoLi,                     | PedramGhamisi, | Xi- |
| ------------- | ------------------ | --- | -------------- | --------------- | ------- | ----------- | -------------- | --- | ------------ | --- | -------------------------- | -------------- | --- |
| [5] Hao Chen, | Zhenghong          |     | Li, Jiangjiang |                 | Wu, Wei | Xiong, and  |                |     |              |     |                            |                |     |
|               |                    |     |                |                 |         |             | upingJia,etal. |     | Spectralgpt: |     | Spectralremotesensingfoun- |                |     |
| Chun          | Du. Semiroadexnet: |     | A              | semi-supervised |         | network for |                |     |              |     |                            |                |     |
road extraction from remote sensing imagery via adversar- dation model. IEEE Transactions on Pattern Analysis and
iallearning. ISPRSJournalofPhotogrammetryandRemote MachineIntelligence,2024. 4
Sensing,198:169–183,2023. 3 [17] Jared Kaplan, Sam McCandlish, Tom Henighan, Tom B
|                |      |       |       |             |     |            | Brown, | Benjamin | Chess, | Rewon | Child, | Scott | Gray, Alec |
| -------------- | ---- | ----- | ----- | ----------- | --- | ---------- | ------ | -------- | ------ | ----- | ------ | ----- | ---------- |
| [6] Ziyi Chen, | Liai | Deng, | Yuhua | Luo, Dilong | Li, | Jose´ Mar- |        |          |        |       |        |       |            |
catoJunior,WesleyNunesGonc¸alves,AbdulAwalMdNu- Radford, Jeffrey Wu, and Dario Amodei. Scaling laws for
runnabi,JonathanLi,ChengWang,andDerenLi. Roadex- neurallanguagemodels. arXivpreprintarXiv:2001.08361,
| tractioninremotesensingdata:Asurvey.Internationaljour- |         |                   |     |     |                 |      | 2020.     | 2           |      |           |       |           |            |
| ------------------------------------------------------ | ------- | ----------------- | --- | --- | --------------- | ---- | --------- | ----------- | ---- | --------- | ----- | --------- | ---------- |
|                                                        |         |                   |     |     |                 |      | [18] Teja | Kattenborn, | Jens | Leitloff, | Felix | Schiefer, | and Stefan |
| nal of                                                 | applied | earth observation |     | and | geoinformation, | 112: |           |             |      |           |       |           |            |
Hinz.Reviewonconvolutionalneuralnetworks(cnn)inveg-
| 102833,2022. |     | 1   |     |     |     |     |     |     |     |     |     |     |     |
| ------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
[7] Guangliang Cheng, Ying Wang, Shibiao Xu, Hongzhen etation remote sensing. ISPRS journal of photogrammetry
|                                   |     |     |     |     |               |     | andremotesensing,173:24–49,2021. |     |     |     |     | 3   |     |
| --------------------------------- | --- | --- | --- | --- | ------------- | --- | -------------------------------- | --- | --- | --- | --- | --- | --- |
| Wang,ShimingXiang,andChunhongPan. |     |     |     |     | Automaticroad |     |                                  |     |     |     |     |     |     |
[19] AlexanderKirillov,EricMintun,NikhilaRavi,HanziMao,
detectionandcenterlineextractionviacascadedend-to-end
ChloeRolland,LauraGustafson,TeteXiao,SpencerWhite-
| convolutional                                 |           | neural network. |           | IEEE Transactions |             | on Geo- |                                              |                                             |     |     |     |     |             |
| --------------------------------------------- | --------- | --------------- | --------- | ----------------- | ----------- | ------- | -------------------------------------------- | ------------------------------------------- | --- | --- | --- | --- | ----------- |
|                                               |           |                 |           |                   |             |         | head,AlexanderCBerg,Wan-YenLo,etal.          |                                             |     |     |     |     | Segmentany- |
| scienceandRemoteSensing,55(6):3322–3337,2017. |           |                 |           |                   |             | 3       |                                              |                                             |     |     |     |     |             |
|                                               |           |                 |           |                   |             |         | thing.                                       | InProceedingsoftheIEEE/CVFInternationalCon- |     |     |     |     |             |
| [8] Ilke Demir,                               | Krzysztof |                 | Koperski, | David             | Lindenbaum, | Guan    |                                              |                                             |     |     |     |     |             |
|                                               |           |                 |           |                   |             |         | ferenceonComputerVision,pages4015–4026,2023. |                                             |     |     |     |     | 4           |
Pang,JingHuang,SaikatBasu,ForestHughes,DevisTuia,
|                  |         |                |         |     |                   |        | [20] Yann | LeCun,                         | Yoshua | Bengio, | and Geoffrey | Hinton. | Deep |
| ---------------- | ------- | -------------- | ------- | --- | ----------------- | ------ | --------- | ------------------------------ | ------ | ------- | ------------ | ------- | ---- |
| andRameshRaskar. |         | Deepglobe2018: |         |     | Achallengetoparse |        |           |                                |        |         |              |         |      |
|                  |         |                |         |     |                   |        | learning. | nature,521(7553):436–444,2015. |        |         |              | 3       |      |
| the earth        | through | satellite      | images. | In  | Proceedings       | of the |           |                                |        |         |              |         |      |
IEEEconferenceoncomputervisionandpatternrecognition [21] JesseLevinson,JakeAskeland,JanBecker,JenniferDolson,
|                              |         |                                  |       |       |          |          | David                                         | Held,                 | Soeren | Kammel, | J Zico                 | Kolter, | Dirk Langer, |
| ---------------------------- | ------- | -------------------------------- | ----- | ----- | -------- | -------- | --------------------------------------------- | --------------------- | ------ | ------- | ---------------------- | ------- | ------------ |
| workshops,pages172–181,2018. |         |                                  |       | 2,3   |          |          |                                               |                       |        |         |                        |         |              |
|                              |         |                                  |       |       |          |          | OliverPink,VaughanPratt,etal.                 |                       |        |         | Towardsfullyautonomous |         |              |
| [9] Vikas                    | Dhiman, | Quoc-Huy                         | Tran, | Jason | J Corso, | and Man- |                                               |                       |        |         |                        |         |              |
|                              |         |                                  |       |       |          |          | driving:                                      | Systemsandalgorithms. |        |         | In2011IEEEintelligent  |         |              |
| mohanChandraker.             |         | Acontinuousocclusionmodelforroad |       |       |          |          |                                               |                       |        |         |                        |         |              |
|                              |         |                                  |       |       |          |          | vehiclessymposium(IV),pages163–168.IEEE,2011. |                       |        |         |                        |         | 1            |
sceneunderstanding.InProceedingsoftheIEEEConference
|             |     |            |         |              |     |             | [22] QiLi,YueWang,YilunWang,andHangZhao. |     |     |     |     |     | Hdmapnet: |
| ----------- | --- | ---------- | ------- | ------------ | --- | ----------- | ---------------------------------------- | --- | --- | --- | --- | --- | --------- |
| on Computer |     | Vision and | Pattern | Recognition, |     | pages 4331– |                                          |     |     |     |     |     |           |
Anonlinehdmapconstructionandevaluationframework.In
| 4339,2016. | 2   |     |     |     |     |     |     |     |     |     |     |     |     |
| ---------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
2022InternationalConferenceonRoboticsandAutomation
[10] XunGao, XianSun, YiZhang, MenglongYan, Guangluan (ICRA),pages4628–4634.IEEE,2022. 3
Xu,HaoSun,JiaoJiao,andKunFu. Anend-to-endneural [23] Yue Li, Rong Zhang, and Yunfei Wu. Road network ex-
networkforroadextractionfromremotesensingimageryby
|                                |     |     |     |             |     |          | tractioninhigh-resolutionsarimagesbasedcnnfeatures. |                    |     |            |     |            | In      |
| ------------------------------ | --- | --- | --- | ----------- | --- | -------- | --------------------------------------------------- | ------------------ | --- | ---------- | --- | ---------- | ------- |
| multiplefeaturepyramidnetwork. |     |     |     | IEEEAccess, |     | 6:39401– |                                                     |                    |     |            |     |            |         |
|                                |     |     |     |             |     |          | 2017                                                | IEEE International |     | Geoscience |     | and Remote | Sensing |
| 39414,2018.                    |     | 3   |     |             |     |          |                                                     |                    |     |            |     |            |         |
|                                |     |     |     |             |     |          | Symposium(IGARSS),pages1664–1667.IEEE,2017.         |                    |     |            |     |            | 3       |
[11] YanmingGuo,YuLiu,ArdOerlemans,SongyangLao,Song [24] ZewenLi, FanLiu, WenjieYang, ShouhengPeng, andJun
Wu, and Michael S Lew. Deep learning for visual under- Zhou. Asurveyofconvolutionalneuralnetworks: analysis,
| standing:Areview. |     | Neurocomputing,187:27–48,2016. |     |     |     | 3   |               |     |                |     |                   |     |           |
| ----------------- | --- | ------------------------------ | --- | --- | --- | --- | ------------- | --- | -------------- | --- | ----------------- | --- | --------- |
|                   |     |                                |     |     |     |     | applications, |     | and prospects. |     | IEEE transactions |     | on neural |
[12] MordechaiHaklayandPatrickWeber.Openstreetmap:User- networksandlearningsystems,33(12):6999–7019,2021. 3
9

[25] Tsung-Yi Lin, Piotr Dolla´r, Ross Girshick, Kaiming He, [40] AdamVanEtten,DaveLindenbaum,andToddMBacastow.
Bharath Hariharan, and Serge Belongie. Feature pyra- Spacenet: A remote sensing dataset and challenge series.
mid networks for object detection. In Proceedings of the arXivpreprintarXiv:1807.01232,2018. 2,3,6
IEEE conference on computer vision and pattern recogni- [41] AVaswani. Attentionisallyouneed. AdvancesinNeural
tion,pages2117–2125,2017. 3 InformationProcessingSystems,2017. 3
[26] YenengLin,DongyunXu,NanWang,ZhouShi,andQiux- [42] PeijuanWang, BulentBayram, andElifSertel. Acompre-
iaoChen.Roadextractionfromvery-high-resolutionremote hensive review on deep learning based remote sensing im-
sensingimagesviaanestedse-deeplabmodel.Remotesens- agesuper-resolutionmethods. Earth-ScienceReviews,232:
| ing,12(18):2985,2020. |     | 3   |     |     |     | 104110,2022. | 1   |     |     |     |
| --------------------- | --- | --- | --- | --- | --- | ------------ | --- | --- | --- | --- |
[27] Richard J Lisle. Google earth: a new geological resource. [43] ZhouWang,AlanCBovik,HamidRSheikh,andEeroPSi-
Geologytoday,22(1):29–32,2006. 3 moncelli. Imagequalityassessment: fromerrorvisibilityto
[28] Ruyi Liu, Junhong Wu, Wenyi Lu, Qiguang Miao, Huan structuralsimilarity.IEEEtransactionsonimageprocessing,
Zhang,XiangzengLiu,ZixiangLu,andLongLi. Areview 13(4):600–612,2004. 3
|         |                |         |          |            |      | [44] Jason | Wei, Yi Tay, Rishi | Bommasani, | Colin | Raffel, Barret |
| ------- | -------------- | ------- | -------- | ---------- | ---- | ---------- | ------------------ | ---------- | ----- | -------------- |
| of deep | learning-based | methods | for road | extraction | from |            |                    |            |       |                |
Zoph,SebastianBorgeaud,DaniYogatama,MaartenBosma,
| high-resolutionremotesensingimages. |     |     |     | RemoteSensing,16 |     |     |     |     |     |     |
| ----------------------------------- | --- | --- | --- | ---------------- | --- | --- | --- | --- | --- | --- |
(12):2056,2024. 3 Denny Zhou, Donald Metzler, et al. Emergent abilities of
|     |     |     |     |     |     | large language | models. | arXiv | preprint | arXiv:2206.07682, |
| --- | --- | --- | --- | --- | --- | -------------- | ------- | ----- | -------- | ----------------- |
[29] FannyMalin,IlkkaNorros,andSatuInnamaa.Accidentrisk
|                                                 |     |     |     |     |     | 2022. | 2   |     |     |     |
| ----------------------------------------------- | --- | --- | --- | --- | --- | ----- | --- | --- | --- | --- |
| ofroadandweatherconditionsondifferentroadtypes. |     |     |     |     | Ac- |       |     |     |     |     |
[45] ZhenhuaXu,YuxuanLiu,LuGan,YuxiangSun,XinyuWu,
| cidentAnalysis&Prevention,122:181–188,2019. |     |               |              |     | 2         |           |           |               |      |               |
| ------------------------------------------- | --- | ------------- | ------------ | --- | --------- | --------- | --------- | ------------- | ---- | ------------- |
|                                             |     |               |              |     |           | Ming Liu, | and Lujia | Wang. Rngdet: | Road | network graph |
| [30] GellertMattyus,                        |     | ShenlongWang, | SanjaFidler, |     | andRaquel |           |           |               |      |               |
detectionbytransformerinaerialimages.IEEETransactions
| Urtasun.        | Enhancing | road maps                           | by parsing | aerial | images |                                            |     |     |     |        |
| --------------- | --------- | ----------------------------------- | ---------- | ------ | ------ | ------------------------------------------ | --- | --- | --- | ------ |
|                 |           |                                     |            |        |        | onGeoscienceandRemoteSensing,60:1–12,2022. |     |     |     | 1,3,6, |
| aroundtheworld. |           | InProceedingsoftheIEEEinternational |            |        |        |                                            |     |     |     |        |
7
| conferenceoncomputervision,pages1689–1697,2015. |     |     |     |     | 2   |     |     |     |     |     |
| ----------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
[46] ZhenhuaXu,YuxuanLiu,YuxiangSun,MingLiu,andLujia
| [31] VolodymyrMnih.                    |     | Machinelearningforaerialimagelabel- |     |     |     |       |                                             |     |     |     |
| -------------------------------------- | --- | ----------------------------------- | --- | --- | --- | ----- | ------------------------------------------- | --- | --- | --- |
|                                        |     |                                     |     |     |     | Wang. | Rngdet++: Roadnetworkgraphdetectionbytrans- |     |     |     |
| ing. UniversityofToronto(Canada),2013. |     |                                     |     | 2,3 |     |       |                                             |     |     |     |
formerwithinstancesegmentationandmulti-scalefeatures
| [32] Sherif | AS Mohamed, | Mohammad-Hashem |     |     | Haghbayan, |              |                                        |     |     |     |
| ----------- | ----------- | --------------- | --- | --- | ---------- | ------------ | -------------------------------------- | --- | --- | --- |
|             |             |                 |     |     |            | enhancement. | IEEERoboticsandAutomationLetters,8(5): |     |     |     |
TomiWesterlund, JukkaHeikkonen, HannuTenhunen, and 2991–2998,2023. 1,3,6,7
| JuhaPlosila. | Asurveyonodometryforautonomousnaviga- |     |     |     |     |            |                        |              |      |                    |
| ------------ | ------------------------------------- | --- | --- | --- | --- | ---------- | ---------------------- | ------------ | ---- | ------------------ |
|              |                                       |     |     |     |     | [47] Ruoyu | Yang, Yanfei           | Zhong, Yinhe | Liu, | Xiaoyan Lu, and    |
| tionsystems. | IEEEaccess,7:97466–97486,2019.        |     |     |     | 1   |            |                        |              |      |                    |
|              |                                       |     |     |     |     | Liangpei   | Zhang. Occlusion-aware |              | road | extraction network |
[33] AlbertoMoreira,PauPrats-Iraola,MarwanYounis,Gerhard forhigh-resolutionremotesensingimagery. IEEETransac-
Krieger,IrenaHajnsek,andKonstantinosPPapathanassiou. tionsonGeoscienceandRemoteSensing,2024. 2
| Atutorialonsyntheticapertureradar. |     |     | IEEEGeoscienceand |     |     |     |     |     |     |     |
| ---------------------------------- | --- | --- | ----------------- | --- | --- | --- | --- | --- | --- | --- |
[48] LiYuan,YunpengChen,TaoWang,WeihaoYu,YujunShi,
| remotesensingmagazine,1(1):6–43,2013. |     |     |     | 3   |     |     |     |     |     |     |
| ------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
Zi-HangJiang,FrancisEHTay,JiashiFeng,andShuicheng
[34] Onisimo Mutanga and Lalit Kumar. Google earth engine Yan. Tokens-to-tokenvit:Trainingvisiontransformersfrom
applications,2019. 3 scratch on imagenet. In Proceedings of the IEEE/CVF in-
[35] Ilja Nastjuk, Bernd Herrenkind, Mauricio Marrone, Al- ternationalconferenceoncomputervision,pages558–567,
| fredBenediktBrendel,andLutzMKolbe. |     |     |     | Whatdrivesthe |     | 2021. | 3   |     |     |     |
| ---------------------------------- | --- | --- | --- | ------------- | --- | ----- | --- | --- | --- | --- |
acceptance of autonomous driving? an investigation of ac- [49] Ekim Yurtsever, Jacob Lambert, Alexander Carballo, and
ceptancefactorsfromanend-user’sperspective. Technolog- KazuyaTakeda. Asurveyofautonomousdriving:Common
icalForecastingandSocialChange,161:120319,2020. 1 practicesandemergingtechnologies.IEEEaccess,8:58443–
| [36] LucasPradoOsco,QiushengWu,EduardoLopesdeLemos, |     |     |     |     |     | 58469,2020. | 1   |     |     |     |
| --------------------------------------------------- | --- | --- | --- | --- | --- | ----------- | --- | --- | --- | --- |
Wesley Nunes Gonc¸alves, Ana Paula Marques Ramos, [50] TongjieYZhangandChingY.Suen. Afastparallelalgo-
JonathanLi,andJose´MarcatoJunior.Thesegmentanything rithm for thinning digital patterns. Communications of the
model(sam)forremotesensingapplications: Fromzeroto ACM,27(3):236–239,1984. 3
oneshot. InternationalJournalofAppliedEarthObserva- [51] Qiqi Zhu, Yanan Zhang, Lizeng Wang, Yanfei Zhong,
tionandGeoinformation,124:103540,2023. 4 QingfengGuan,XiaoyanLu,LiangpeiZhang,andDerenLi.
[37] Zehang Sun, George Bebis, and Ronald Miller. On-road A global context-aware and batch-independent network for
IEEEtransactionsonpattern roadextractionfromvhrsatelliteimagery. ISPRSJournalof
| vehicledetection: |     | Areview. |     |     |     |     |     |     |     |     |
| ----------------- | --- | -------- | --- | --- | --- | --- | --- | --- | --- | --- |
analysisandmachineintelligence,28(5):694–711,2006. 3 Photogrammetry and Remote Sensing, 175:353–365, 2021.
| [38] GabrielSvennerberg.BeginninggooglemapsAPI3.Apress, |     |     |     |     |     | 2,3 |     |     |     |     |
| ------------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
2010. 3 [52] AlesˇZˇnidaricˇ,VikramPakrashi,EugeneO’Brien,andAlan
|                                                       |     |     |     |     |      | O’Connor. | Areviewofroadstructuredatainsixeuropean |     |     |     |
| ----------------------------------------------------- | --- | --- | --- | --- | ---- | --------- | --------------------------------------- | --- | --- | --- |
| [39] MichailTarasiou,ErikChavez,andStefanosZafeiriou. |     |     |     |     | Vits |           |                                         |     |     |     |
forsits: Visiontransformersforsatelliteimagetimeseries. countries. ProceedingsoftheInstitutionofCivilEngineers-
In Proceedings of the IEEE/CVF Conference on Computer Urbandesignandplanning,164(4):225–232,2011. 3
VisionandPatternRecognition,pages10418–10428,2023.
3
10