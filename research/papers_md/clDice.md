clDice - a Novel Topology-Preserving Loss Function for Tubular Structure
Segmentation
SuprosannaShit*1 JohannesC.Paetzold∗ 1 AnjanySekuboyina1 IvanEzhov1
AlexanderUnger1 AndreyZhylka2 JosienP.W.Pluim2 UlrichBauer1 BjoernH.Menze1
1TechnicalUniversityofMunich 2 EindhovenUniversityofTechnology
2202 luJ 51  ]VC.sc[  7v11370.3002:viXra
Abstract
| Accurate    | segmentation |          | of       | tubular,         | network-like | struc-       |     |     |     |     |     |     |     |
| ----------- | ------------ | -------- | -------- | ---------------- | ------------ | ------------ | --- | --- | --- | --- | --- | --- | --- |
| tures, such | as           | vessels, | neurons, | or roads,        | is           | relevant to  |     |     |     |     |     |     |     |
| many fields | of research. |          | For      | such structures, |              | the topology |     |     |     |     |     |     |     |
istheirmostimportantcharacteristic;particularlypreserv-
| ingconnectedness: |     | inthecaseofvascularnetworks,miss- |     |     |     |     |     |     |     |     |     |     |     |
| ----------------- | --- | --------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
ingaconnectedvesselentirelyalterstheblood-flowdynam-
ics. Weintroduceanovelsimilaritymeasuretermedcenter-
| lineDice       | (short           | clDice),      | which | is calculated |             | on the inter- |     |     |     |     |     |     |     |
| -------------- | ---------------- | ------------- | ----- | ------------- | ----------- | ------------- | --- | --- | --- | --- | --- | --- | --- |
| section of     | the segmentation |               | masks | and           | their       | (morpholog-   |     |     |     |     |     |     |     |
| ical) skeleta. | We               | theoretically |       | prove         | that clDice | guaran-       |     |     |     |     |     |     |     |
teestopologypreservationuptohomotopyequivalencefor
| binary 2D              | and | 3D segmentation. |            | Extending       |        | this, we pro- |     |     |     |     |     |     |     |
| ---------------------- | --- | ---------------- | ---------- | --------------- | ------ | ------------- | --- | --- | --- | --- | --- | --- | --- |
| pose a computationally |     |                  | efficient, | differentiable  |        | loss func-    |     |     |     |     |     |     |     |
| tion (soft-clDice)     |     | for training     |            | arbitrary       | neural | segmenta-     |     |     |     |     |     |     |     |
| tion networks.         |     | We benchmark     |            | the soft-clDice |        | loss on five  |     |     |     |     |     |     |     |
| public datasets,       |     | including        | vessels,   | roads           | and    | neurons (2D   |     |     |     |     |     |     |     |
Figure1.Motivation:Thefigureshowsa3Drenderingofacom-
and3D).Trainingonsoft-clDiceleadstosegmentationwith
|     |     |     |     |     |     |     | plex, whole | brain | vascular | dataset | [50], where | an  | exemplary 2D |
| --- | --- | --- | --- | --- | --- | --- | ----------- | ----- | -------- | ------- | ----------- | --- | ------------ |
moreaccurateconnectivityinformation,highergraphsimi- sliceofthedataischosenandsegmentedbytwodifferentmodels,
larity,andbettervolumetricscores. seepurple(middle)andred(right),respectively.Thetwosegmen-
|     |     |     |     |     |     |     | tation results | achieve | identical | quality | in terms | of  | the traditional |
| --- | --- | --- | --- | --- | --- | --- | -------------- | ------- | --------- | ------- | -------- | --- | --------------- |
Dicescore.Notethatthepurplesegmentationdoesnotcapturethe
1.Introduction small vessels while segmenting the large vessel very accurately;
ontheotherside,theredsegmentationcapturesallvesselsinthe
Segmentationoftubularandcurvilinearstructuresisan imagewhilebeinglessaccurateontheradiusofthelargevessel.
essential problem in numerous domains, such as clinical Skeletaaredrawninyellow.Fromatopologyornetworkperspec-
and biological applications (blood vessel and neuron seg- tive,theredsegmentationisevidentlypreferred.
mentationfrommicroscopic,optoacoustic,orradiologyim-
|               |                |         |              |            |               |          | tures, are    | 1) overlap | based            | measures | such            | as         | Dice, preci- |
| ------------- | -------------- | ------- | ------------ | ---------- | ------------- | -------- | ------------- | ---------- | ---------------- | -------- | --------------- | ---------- | ------------ |
| ages), remote | sensing        |         | applications | (road      | network       | segmen-  |               |            |                  |          |                 |            |              |
|               |                |         |              |            |               |          | sion, recall, | and        | Jaccard          | index;   | and 2)          | volumetric | distance     |
| tation from   | satellite      | images) | and          | industrial | quality       | control, |               |            |                  |          |                 |            |              |
|               |                |         |              |            |               |          | measures      | such       | as the Hausdorff |          | and Mahalanobis |            | distance     |
| etc. In the   | aforementioned |         | domains,     | a          | topologically | accu-    |               |            |                  |          |                 |            |              |
[21,42,37,16].
ratesegmentationisnecessarytoguaranteeerror-freedown-
|                |             |                                       |                 |               |             |           | However,                                        | in                                       | most segmentation |          | problems,      |               | where the    |
| -------------- | ----------- | ------------------------------------- | --------------- | ------------- | ----------- | --------- | ----------------------------------------------- | ---------------------------------------- | ----------------- | -------- | -------------- | ------------- | ------------ |
| stream tasks,  | such        | as computational                      |                 | hemodynamics, |             | route     |                                                 |                                          |                   |          |                |               |              |
|                |             |                                       |                 |               |             |           | object of                                       | interest                                 | is 1)             | locally  | a tubular      | structure     | and 2)       |
| planning,      | Alzheimer’s |                                       | disease         | prediction    | [18],       | or stroke |                                                 |                                          |                   |          |                |               |              |
|                |             |                                       |                 |               |             |           | globally                                        | forms                                    | a network,        | the      | most important |               | characteris- |
| modeling[20].  |             | Whenoptimizingcomputationalalgorithms |                 |               |             |           |                                                 |                                          |                   |          |                |               |              |
|                |             |                                       |                 |               |             |           | ticistheconnectivityoftheglobalnetworktopology. |                                          |                   |          |                |               | Note         |
| for segmenting |             | curvilinear                           | structures,     |               | the two     | most com- |                                                 |                                          |                   |          |                |               |              |
|                |             |                                       |                 |               |             |           | thatnetwork                                     | inthiscontextimpliesaphysicallyconnected |                   |          |                |               |              |
| monly used     | categories  |                                       | of quantitative |               | performance | mea-      |                                                 |                                          |                   |          |                |               |              |
|                |             |                                       |                 |               |             |           | structure,                                      | such                                     | as a vessel       | network, | a              | road network, | etc.,        |
suresforevaluatingsegmentationaccuracyoftubularstruc-
whichisalsotheprimarystructureofinterestforthegiven
*Theauthorscontributedequallytothework imagedata. Asanexample,onecanrefertobrainvascula-

tureanalysis,whereamissedvesselsegmentinthesegmen- priorstonaturalimages[2],higher-ordercliqueswhichcon-
tation mask can pathologically be interpreted as a stroke nectsuperpixels[55]andadversariallearningforroadseg-
or may lead to dramatic changes in a global simulation mentation [53], integer programming to general curvilin-
of blood flow. On the other hand, limited over- or under- earstructures[51],andproposedatree-structuredconvolu-
segmentation of vessel radius can be tolerated, because it tionalgatedrecurrentunit[22],morphologicaloptimization
doesnotaffectclinicaldiagnosis. [14], among others [3, 15, 32, 31, 34, 38, 43, 54, 59, 58].
For evaluating segmentations in such tubular-network Further, topological priors of containment were applied to
structures, traditional volume-based performance indices histology scans [5], a 3D CNN with graph refinement was
are sub-optimal. For example, Dice and Jaccard rely on used to improve airway connectivity [19], and recently,
|                                              |     |     |     |     |     |         | Mosinska | et al. | trained | networks | which | perform | segmen- |
| -------------------------------------------- | --- | --- | --- | --- | --- | ------- | -------- | ------ | ------- | -------- | ----- | ------- | ------- |
| theaveragevoxel-wisehitormissprediction[48]. |     |     |     |     |     | Inatask |          |        |         |          |       |         |         |
likenetwork-topologyextraction,aspatiallycontiguousse- tationandpathclassificationsimultaneously[30]. Another
quenceofcorrectvoxelpredictionismoremeaningfulthan approachenablesthepredefinitionofBettinumbersanden-
aspuriouscorrectprediction. Thisambiguityisrelevantfor forcesthemonthetraining[8].
objects of interest, which are of the same thickness as the The aforementioned literature has advanced the com-
resolutionofthesignal. Forthem,itisevidentthatasingle- munities understanding of topology-preservation, but crit-
voxelshiftinthepredictioncanchangethetopologyofthe ically, they do not possess end-to-end loss functions that
whole network. Further, a globally averaged metric does optimize topology-preservation. In this context, the litera-
|             |        |                    |     |      |        |         | ture remains | sparse. | Recently, |     | Mosinska | et al. | suggested |
| ----------- | ------ | ------------------ | --- | ---- | ------ | ------- | ------------ | ------- | --------- | --- | -------- | ------ | --------- |
| not equally | weight | tubular-structures |     | with | large, | medium, |              |         |           |     |          |        |           |
and small radii (cf. Fig 1). In real vessel datasets, where that pixel-wise loss-functions are unsuitable and used se-
vessels of wide radius ranges exist, e.g. 30 µm for arteri- lected filter responses from a VGG19 network as an addi-
olesand5µmforcapillaries[50,9],trainingonaglobally tional penalty [29]. Nonetheless, their approach does not
averaged loss induces a strong bias towards the volumet- prove topology preservation. Importantly, Hu et al. pro-
posedthefirstcontinuous-valuedlossfunctionbasedonthe
| ric segmentation |     | of large | vessels. | Both | scenarios | are pro- |     |     |     |     |     |     |     |
| ---------------- | --- | -------- | -------- | ---- | --------- | -------- | --- | --- | --- | --- | --- | --- | --- |
nounced in imaging modalities, such as fluorescence mi- Bettinumberandpersistenthomology[17]. However, this
croscopy[50,60]andoptoacoustics, whichfocusonmap- methodisbasedonmatchingcriticalpoints,which,accord-
pingsmallcapillarystructures. ing to the authors makes the training very expensive and
Tothisend,weareinterestedinatopology-awareimage error-proneforrealimage-sizedpatches[17]. Whilethisis
alreadylimitingforatranslationtolargerealworlddataset,
segmentation,eventuallyenablingacorrectnetworkextrac-
tion. Therefore,weaskthefollowingresearchquestions: we find that none of these approaches have been extended
tothreedimensional(3D)data.
| Q1. What | is a | good pixelwise |     | measure | to benchmark | seg- |     |     |     |     |     |     |     |
| -------- | ---- | -------------- | --- | ------- | ------------ | ---- | --- | --- | --- | --- | --- | --- | --- |
1.2.OurContributions
| mentation |             | algorithms | for | tubular,     | and related | linear  |               |     |         |       |                |     |               |
| --------- | ----------- | ---------- | --- | ------------ | ----------- | ------- | ------------- | --- | ------- | ----- | -------------- | --- | ------------- |
| and       | curvilinear | structure  |     | segmentation | while       | guaran- |               |     |         |       |                |     |               |
|           |             |            |     |              |             |         | The objective |     | of this | paper | is to identify |     | an efficient, |
teeingthepreservationofthenetwork-topology? general, and intuitive loss function that enables topology
|     |     |     |     |     |     |     | preservation | while | segmenting |     | tubular | objects. | We intro- |
| --- | --- | --- | --- | --- | --- | --- | ------------ | ----- | ---------- | --- | ------- | -------- | --------- |
Q2. Can we use this improved measure as a loss function duceanovelconnectivity-awaresimilaritymeasurenamed
forneuralnetworks,whichisavoidinexistinglitera- clDice for benchmarking tubular-segmentation algorithms.
ture?
Importantly,weprovidetheoreticalguaranteesforthetopo-
logicalcorrectnessoftheclDiceforbinary2Dand3Dseg-
1.1.RelatedLiterature mentation. As a consequence of its formulation based on
|                 |          |               |              |              |            |           | morphological   |     | skeletons, | our measure | pronounces |     | the net-     |
| --------------- | -------- | ------------- | ------------ | ------------ | ---------- | --------- | --------------- | --- | ---------- | ----------- | ---------- | --- | ------------ |
| Achieving       | topology |               | preservation | can          | be crucial | to ob-    |                 |     |            |             |            |     |              |
|                 |          |               |              |              |            |           | work’s topology |     | instead    | of equally  | weighting  |     | every voxel. |
| tain meaningful |          | segmentation, |              | particularly | for        | elongated |                 |     |            |             |            |     |              |
Usingadifferentiablesoft-skeletonization,weshowthatthe
| and connected |     | shapes, | e.g. vascular | structures |     | or roads. |                |     |             |     |              |           |     |
| ------------- | --- | ------- | ------------- | ---------- | --- | --------- | -------------- | --- | ----------- | --- | ------------ | --------- | --- |
|               |     |         |               |            |     |           | clDice measure |     | can be used | to  | train neural | networks. | We  |
However,analyzingpreservationoftopologywhilesimpli-
|     |     |     |     |     |     |     | show experimental |     | results | for various | 2D  | and | 3D network |
| --- | --- | --- | --- | --- | --- | --- | ----------------- | --- | ------- | ----------- | --- | --- | ---------- |
fyinggeometriesisadifficultanalyticalandcomputational
segmentationtaskstodemonstratethepracticalapplicabil-
problem[11,10].
ityofourproposedsimilaritymeasureandlossfunction.
Forbinarygeometries,variousalgorithmsbasedonthin-
ningandmedialsurfaceshavebeenproventobetopology- 2.Let’sEmphasizeConnectivity
| preserving | according |     | to varying | definitions | of  | topology |     |     |     |     |     |     |     |
| ---------- | --------- | --- | ---------- | ----------- | --- | -------- | --- | --- | --- | --- | --- | --- | --- |
[23,25,26,36]. Fornon-binarygeometries,existingmeth- We propose a novel connectivity-preserving metric to
odsappliedtopologyandconnectivityconstraintsontovari- evaluatetubularandlinearstructuresegmentationbasedon
ationalandMarkovrandomfield-basedmethods:treeshape intersectingskeletonswithmasks. Wecallthismetriccen-
priors for vessel segmentation [46], graph representation terlineDiceorclDice.

Figure2. Schematicoverviewofourproposedmethod:OurproposedclDicelosscanbeappliedtoanyarbitrarysegmentationnetwork.
Thesoft-skeletonizationcanbeeasilyimplementedusingpoolingfunctionsfromanystandarddeep-learningtoolbox.
We consider two binary masks: the ground truth mask achievedbyoptimizingclDiceundermildconditionsonthe
(V )andthepredictedsegmentationmasks(V
L P ). First,the input. Roughly,theseconditionsstatethattheobjectofin-
skeletons S and S are extracted from V and V re- terest is embedded in S3 in a non-knotted way, as is typi-
|     |     | P   | L   |     |     | P   | L   |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
spectively. Subsequently, we compute the fraction of S callythecaseforbloodvesselandroadstructures.
P
| that    | lies within | V L                                    | , which | we call | Topology | Precision | or  |               |     |           |      |      |        |           |
| ------- | ----------- | -------------------------------------- | ------- | ------- | -------- | --------- | --- | ------------- | --- | --------- | ---- | ---- | ------ | --------- |
|         |             |                                        |         |         |          |           |     | Specifically, |     | we assume | that | both | ground | truth and |
| Tprec(S | ,V          | ), andvice-a-versaweobtainTopologySen- |         |         |          |           |     |               |     |           |      |      |        |           |
|         | P           | L                                      |         |         |          |           |     |               |     |           |      |      |        |           |
sitivityorTsens(S ,V )asdefinedbellow; prediction admit foreground and background skeleta,
|     |     | L   | P   |     |     |     |     |             |      |      |            |     |            |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ----------- | ---- | ---- | ---------- | --- | ---------- | --- |
|     |     |     |     |     |     |     |     | which means | that | both | foreground | and | background | are |
|S P ∩V L | |S L ∩V P | homotopy-equivalent to topological graphs, which we
| Tprec(S | ,V  | )=  |     | ; Tsens(S |     | ,V )= |     |     |     |     |     |     |     |     |
| ------- | --- | --- | --- | --------- | --- | ----- | --- | --- | --- | --- | --- | --- | --- | --- |
P L |S | L P |S | assume to be embedded as skeleta. Here, the voxel grid is
|     |     |     | P   |     |     |     | L   |            |      |                  |     |            |     |            |
| --- | --- | --- | --- | --- | --- | --- | --- | ---------- | ---- | ---------------- | --- | ---------- | --- | ---------- |
|     |     |     |     |     |     |     |     | considered | as a | cubical complex, |     | consisting | of  | elementary |
(1)
|     |     |     |     |     |     |     |     | cubes of dimensions |     | 0, 1, | 2, and | 3. This | is a special | case |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------------- | --- | ----- | ------ | ------- | ------------ | ---- |
We observe that the measure Tprec(S ,V ) is suscepti- of a cell complex (specifically, a CW complex), which is a
|        |       |           |        |            | P     | L   |         |                   |     |              |          |      |          |        |
| ------ | ----- | --------- | ------ | ---------- | ----- | --- | ------- | ----------------- | --- | ------------ | -------- | ---- | -------- | ------ |
| ble to | false | positives | in the | prediction | while | the | measure |                   |     |              |          |      |          |        |
|        |       |           |        |            |       |     |         | space constructed |     | inductively, | starting | with | isolated | points |
Tsens(S L ,V P ) is susceptible to false negatives. This ex- (0-cells), and gluing a collection of topological balls of
plainsourrationalebehindreferringtotheTprec(S ,V ) dimension k (called k-cells) along their boundary spheres
|                                      |     |     |     |     |     |               | P L |                            |     |     |     |                      |     |     |
| ------------------------------------ | --- | --- | --- | --- | --- | ------------- | --- | -------------------------- | --- | --- | --- | -------------------- | --- | --- |
| astopology’sprecisionandtotheTsens(S |     |     |     |     |     | ,V )asitssen- |     |                            |     |     |     |                      |     |     |
|                                      |     |     |     |     |     | L P           |     | toak−1-dimensionalcomplex. |     |     |     | Thevoxelgrid,seenasa |     |     |
sitivity. Sincewewanttomaximizebothprecisionandsen- cellcomplexinthissense,canbecompletedtoanambient
| sitivity(recall), |     | wedefineclDicetobetheharmonicmean |     |     |     |     |     |         |         |              |     |        |          | S3  |
| ----------------- | --- | --------------------------------- | --- | --- | --- | --- | --- | ------- | ------- | ------------ | --- | ------ | -------- | --- |
|                   |     |                                   |     |     |     |     |     | complex | that is | homeomorphic |     | to the | 3-sphere | by  |
(alsoknownasF1orDice)ofboththemeasures: attachingasingleexteriorcelltotheboundary. Inorderto
|     |     |     |         |     |                |     |          | consider foreground |     | and | background | of  | a binary | image as |
| --- | --- | --- | ------- | --- | -------------- | --- | -------- | ------------------- | --- | --- | ---------- | --- | -------- | -------- |
|     |     |     | Tprec(S | P   | ,V L )×Tsens(S |     | L ,V P ) |                     |     |     |            |     |          |          |
clDice(V ,V )=2× complementarysubspaces, theforegroundisnowassumed
|     | P   | L   | Tprec(S |     | ,V )+Tsens(S |     | ,V ) |     |     |     |     |     |     |     |
| --- | --- | --- | ------- | --- | ------------ | --- | ---- | --- | --- | --- | --- | --- | --- | --- |
P L L P to be the union of closed unit cubes in the voxel grid,
|     |     |     |     |     |     |     | (2) |                   |     |        |            | 1;       |                |         |
| --- | --- | --- | --- | --- | --- | --- | --- | ----------------- | --- | ------ | ---------- | -------- | -------------- | ------- |
|     |     |     |     |     |     |     |     | corresponding     | to  | voxels | with value | and      | the background |         |
|     |     |     |     |     |     |     |     | is the complement |     | in the | ambient    | complex. | This           | conven- |
NotethatourclDiceformulationisnotdefinedforTprec=
|      |       |                                        |     |     |     |     |     | tion is commonly |        | used in    | digital | topology | [24,        | 23]. The |
| ---- | ----- | -------------------------------------- | --- | --- | --- | --- | --- | ---------------- | ------ | ---------- | ------- | -------- | ----------- | -------- |
| 0and | Tsens | = 0,butcaneasilybeextendedcontinuously |     |     |     |     |     |                  |        |            |         |          |             |          |
|      |       |                                        |     |     |     |     |     | assumption       | on the | background | can     | then     | be replaced | by a     |
withthevalue0.
convenientequivalentcondition,statingthattheforeground
isalsohomotopyequivalenttoasubcomplexobtainedfrom
3.TopologicalGuaranteesforclDice
theambientcomplexbyonlyremoving3-cellsand2-cells.
The following section provides general theoretical Suchasubcomplexisthenclearlyhomotopy-equivalentto
guarantees for the preservation of topological properties thecomplementofa1-complex.

|     |     |     |     |     |     |     |     | by A ⊆ | K , which | compose | to an | isomorphism | between |
| --- | --- | --- | --- | --- | --- | --- | --- | ------ | --------- | ------- | ----- | ----------- | ------- |
B
We will now observe that the above assumptions imply thehomotopygroupsofAandB.
| that the | foreground |             | and the | background |     | are       | connected |               |     |           |                        |     |     |
| -------- | ---------- | ----------- | ------- | ---------- | --- | --------- | --------- | ------------- | --- | --------- | ---------------------- | --- | --- |
|          |            |             |         |            |     |           |           | Corollary1.1. |     | LetV andV | betwobinarymasksadmit- |     |     |
| and have | a free     | fundamental |         | group      | and | vanishing | higher    |               |     | L         | P                      |     |     |
tingforegroundandbackgroundskeleta,suchthatthefore-
| fundamental | groups. |     | In particular, |     | the homotopy |     | type is |                 |     |                  |     |                |      |
| ----------- | ------- | --- | -------------- | --- | ------------ | --- | ------- | --------------- | --- | ---------------- | --- | -------------- | ---- |
|             |         |     |                |     |              |     |         | ground skeleton |     | of V is included | in  | the foreground | of V |
already determined by the first Betti number 1; moreover, L P
|       |          |                |     |     |          |     |            | andviceversa,andsimilarlyforthebackground. |     |      |                              |     | Thenthe |
| ----- | -------- | -------------- | --- | --- | -------- | --- | ---------- | ------------------------------------------ | --- | ---- | ---------------------------- | --- | ------- |
| a map | inducing | an isomorphism |     | in  | homology |     | is already |                                            |     |      |                              |     |         |
|       |          |                |     |     |          |     |            | foregroundsofV                             |     | andV | arehomotopyequivalent,andthe |     |         |
a homotopy equivalence. To see this, first note that both L P
sameistruefortheirbackgrounds.
| foreground | and | background |     | are | assumed | to  | have the |     |     |     |     |     |     |
| ---------- | --- | ---------- | --- | --- | ------- | --- | -------- | --- | --- | --- | --- | --- | --- |
homology of a graph, in particular, homology is trivial in Notethattheinclusionconditioninthiscorollaryissat-
| degree 2. | By Alexander |     | duality | [1], | then, | both | foreground |     |     |     |     |     |     |
| --------- | ------------ | --- | ------- | ---- | ----- | ---- | ---------- | --- | --- | --- | --- | --- | --- |
isfiedifandonlyifclDiceevaluatesto1onbothforeground
andbackgroundhavetrivialreducedcohomologyindegree
|     |     |     |     |     |     |     |     | andbackgroundof(V |     | ,V  | ).  |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ----------------- | --- | --- | --- | --- | --- |
|     |     |     |     |     |     |     |     |                   |     | L P |     |     |     |
0, meaningthattheyareconnected. Thisimpliesthatboth This proof lays the ground for a general interpretation
| have a | free fundamental |     | group | (as | any | connected | graph) |           |      |                     |     |         |               |
| ------ | ---------------- | --- | ----- | --- | --- | --------- | ------ | --------- | ---- | ------------------- | --- | ------- | ------------- |
|        |                  |     |       |     |     |           |        | of clDice | as a | topology preserving |     | metric. | Additionally, |
and vanishing higher homotopy groups. In particular, we provide an elaborate explanation of clDice topological
| since homology |     | in degree |     | 1 is the | Abelianization |     | of the |     |     |     |     |     |     |
| -------------- | --- | --------- | --- | -------- | -------------- | --- | ------ | --- | --- | --- | --- | --- | --- |
properties,usingconceptsofapplieddigitaltopologyinthe
| fundamental | group, |     | these | two groups |     | are isomorphic. |     |     |     |     |     |     |     |
| ----------- | ------ | --- | ----- | ---------- | --- | --------------- | --- | --- | --- | --- | --- | --- | --- |
theorysectionoftheSupplementarymaterial[24,23].
| This in | turn implies | that | in  | our setting | a   | map that | induces |     |     |     |     |     |     |
| ------- | ------------ | ---- | --- | ----------- | --- | -------- | ------- | --- | --- | --- | --- | --- | --- |
isomorphisms in homology already induces isomorphisms 4.TrainingNeuralNetworkswithclDice
| between | all homotopy |     | groups. | By  | Whitehead’s |     | theorem |        |          |         |             |         |           |
| ------- | ------------ | --- | ------- | --- | ----------- | --- | ------- | ------ | -------- | ------- | ----------- | ------- | --------- |
|         |              |     |         |     |             |     |         | In the | previous | section | we provided | general | theoretic |
[56],suchamapisthenahomotopyequivalence.
guaranteeshowclDicehastopologypreservingproperties.
|     |           |         |       |     |            |     |         | The following |     | chapter shows | how we | applied | our theory |
| --- | --------- | ------- | ----- | --- | ---------- | --- | ------- | ------------- | --- | ------------- | ------ | ------- | ---------- |
| The | following | theorem | shows |     | that under | our | assump- |               |     |               |        |         |            |
tions on the images admitting foreground and background to efficiently train topology preserving networks using the
|          |               |     |            |        |            |     |         | clDiceformulation. |     | 2   |     |     |     |
| -------- | ------------- | --- | ---------- | ------ | ---------- | --- | ------- | ------------------ | --- | --- | --- | --- | --- |
| skeleta, | the existence |     | of certain | nested | inclusions |     | already |                    |     |     |     |     |     |
impliesthehomotopy-equivalenceofforegroundandback-
4.1.Soft-clDiceusingSoft-skeletonization:
ground,whichwerefertoastopologypreservation.
Extractingaccurateskeletonsisessentialtoourmethod.
Theorem 1. Let L ⊆ A ⊆ K and L ⊆ B ⊆ K Forthistask,amultitudeofapproacheshasbeenproposed.
|     |     | A   |     | A   |     | B   | B   |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
be connected subcomplexes of some cell complex. Assume However, most of them are not fully differentiable and
thattheaboveinclusionsarehomotopyequivalences. Ifthe therefore unsuited to be used in a loss function. Popular
subcomplexes also are related by inclusions L ⊆ B ⊆ approaches use the Euclidean distance transform or utilize
A
K A and L B ⊆ A ⊆ K B , then these inclusions must be repeatedmorphologicalthinning. Euclideandistancetrans-
homotopyequivalencesaswell. Inparticular,AandB are formhasbeenusedonmultipleoccasions[44,57], butre-
homotopy-equivalent. mains a discrete operation and, to the best of our knowl-
|     |     |     |     |     |     |     |     | edge, an | end-to-end | differentiable | approximation |     | remains |
| --- | --- | --- | --- | --- | --- | --- | --- | -------- | ---------- | -------------- | ------------- | --- | ------- |
Proof. Aninclusionofconnectedcellcomplexesisahomo- to be developed, preventing the use in a loss function for
topyequivalenceifandonlyifitinducesisomorphismson
|     |     |     |     |     |     |     |     | training | neural | networks. | On the contrary, |     | morphological |
| --- | --- | --- | --- | --- | --- | --- | --- | -------- | ------ | --------- | ---------------- | --- | ------------- |
allhomotopygroups. SincetheinclusionL ⊆ B ⊆ K thinning is a sequence of dilation and erosion operations
|         |                 |     |     |           |     | A   | A         |            |     |     |     |     |     |
| ------- | --------------- | --- | --- | --------- | --- | --- | --------- | ---------- | --- | --- | --- | --- | --- |
| induces | an isomorphism, |     | the | inclusion | L   | ⊆   | B induces | [c.f. Fig. | 3]. |     |     |     |     |
A
a monomorphism, and since B ⊆ K B induces an isomor- Importantly, thinning using morphological operations
phism, the inclusion L ⊆ K also induces a monomor- (skeletonization)oncurvilinearstructurescanbetopology-
|        |        |      | A           | B   |           |     |       |                                                   |     |     |     |     |     |
| ------ | ------ | ---- | ----------- | --- | --------- | --- | ----- | ------------------------------------------------- | --- | --- | --- | --- | --- |
| phism. | At the | same | time, since | the | inclusion | L   | ⊆ A ⊆ |                                                   |     |     |     |     |     |
|        |        |      |             |     |           |     | B     | preserving[36].Min-andmaxfiltersarecommonlyusedas |     |     |     |     |     |
K induces an isomorphism, the inclusion A ⊆ K in- thegrey-scalealternativeofmorphologicaldilationandero-
| B   |     |     |     |     |     |     | B   |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
ducesanepiorphism,andsinceL ⊆Ainducesanisomor- sion. Motivatedbythis, wepropose‘soft-skeletonization’,
A
phism,theinclusionL A ⊆K B alsoinducesanepiorphism. where an iterative min- and max-pooling is applied as a
Together,thisimpliesthattheinclusionL ⊆ K induces proxy for morphological erosion and dilation. The Algo-
|     |     |     |     |     |     | A   | B   |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
anisomorphism. rithm1describestheiterativeprocessesinvolvedinitscom-
TogetherwiththeisomorphismsinducedbyL ⊆Aand putation. The hyper-parameter k involved in its computa-
A
B ⊆K ,weobtainisomorphismsinducedbyL ⊆Band tion represents the iterations and has to be greater than or
| B   |     |     |     |     |     |     | A   |                                  |     |     |     |                   |     |
| --- | --- | --- | --- | --- | --- | --- | --- | -------------------------------- | --- | --- | --- | ----------------- | --- |
|     |     |     |     |     |     |     |     | equaltothemaximumobservedradius. |     |     |     | Inourexperiments, |     |
1Betti numbers: β0 represents the number of distinct connected- this parameter depends on the dataset. For example, it is
components,β1representsthenumberofcircularholes,andβ2represents
thenumberofcavities,fordepictionsseeSupplementarymaterial 2https://github.com/jocpae/clDice

|     |     |     | after	i	iterations |     | after	j	iterations |     |     |     | after	k	iterations |     |     |
| --- | --- | --- | ------------------ | --- | ------------------ | --- | --- | --- | ------------------ | --- | --- |
Initial	vessel	structure
Figure3. Basedontheinitialvesselstructure(purple),sequentialbaggingofskeletonvoxels(red)viaiterativeskeletonizationleadstoa
| completeskeletonization,whereddenotesthediameterandk>j |     |     |     | >iiterations. |     |     |     |     |     |     |     |
| ------------------------------------------------------ | --- | --- | --- | ------------- | --- | --- | --- | --- | --- | --- | --- |
Algorithm1:soft-skeleton skeletonized. This enables the extraction of a parameter-
|     |     |     |     | free, morphologically |     |     | motivated | soft-skeleton. |     | The | afore- |
| --- | --- | --- | --- | --------------------- | --- | --- | --------- | -------------- | --- | --- | ------ |
Input:I,k
I(cid:48) mentionedsoft-skeletonizationenablesustouseclDiceasa
←maxpool(minpool(I))
|     |     |     |     | fullydifferentiable, |     | real-valued, |     | optimizablemeasure. |     |     | The |
| --- | --- | --- | --- | -------------------- | --- | ------------ | --- | ------------------- | --- | --- | --- |
S ←ReLU(I−I(cid:48))
|     |     |     |     | Algorithm2describesitsimplementation. |     |     |     |     |     | Werefertothis |     |
| --- | --- | --- | --- | ------------------------------------- | --- | --- | --- | --- | --- | ------------- | --- |
fori←0tokdo
asthesoft-clDice.
I ←minpool(I)
Forasingleconnectedforegroundcomponentandinthe
I(cid:48) ←maxpool(minpool(I))
|     |     |     |     | absence | of knots, | the | homotopy | type | is specified |     | by the |
| --- | --- | --- | --- | ------- | --------- | --- | -------- | ---- | ------------ | --- | ------ |
S ←S+(1−S)◦ReLU(I−I(cid:48))
numberoflinkedloops.Hence,ifthereferenceandthepre-
end
|     |     |     |     | dicted | volumes | are not | homotopy | equivalent, |     | they | do not |
| --- | --- | --- | --- | ------ | ------- | ------- | -------- | ----------- | --- | ---- | ------ |
Output:S
|     |     |     |     | havepairwiselinkedloops. |     |              | Toincludethesemissingloops |     |        |            |     |
| --- | --- | --- | --- | ------------------------ | --- | ------------ | -------------------------- | --- | ------ | ---------- | --- |
|     |     |     |     | or exclude               | the | extra loops, | one                        | has | to add | or discard | de- |
Algorithm2:soft-clDice
|         |                  |     |     | formation | retracted | skeleta       | of  | the solid | foreground. |     | This     |
| ------- | ---------------- | --- | --- | --------- | --------- | ------------- | --- | --------- | ----------- | --- | -------- |
| Input:V | P ,V L           |     |     |           |           |               |     |           |             |     |          |
|         |                  |     |     | implies   | adding    | new correctly |     | predicted | voxels.     | In  | contrast |
| S       | ←soft-skeleton(V | )   |     |           |           |               |     |           |             |     |          |
| P       |                  | P   |     |           |           |               |     |           |             |     |          |
S ←soft-skeleton(V ) toothervolumetriclossessuchasDice,cross-entropy,etc.,
| L       |       | L                |     |        |                |     |                           |     |     |        |     |
| ------- | ----- | ---------------- | --- | ------ | -------------- | --- | ------------------------- | --- | --- | ------ | --- |
|         |       |                  |     | clDice | only considers |     | the deformation-retracted |     |     | graphs | of  |
| Tprec(S | ,V )← | |SP◦VL|+(cid:15) |     |        |                |     |                           |     |     |        |     |
P L |SP|+(cid:15) the solid foreground structure. Thus, we claim that clDice
| Tsens(S | ,V )← | |S L ◦ V P | +(cid:15) |     |     |     |     |     |     |     |     |     |
| ------- | ----- | ---------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
L P | S | + (cid:15) requirestheleastamountofnewcorrectlypredictedvoxels
L
| clDice← |     |     |     | toguaranteethehomotopyequivalence. |     |     |     |     | Alongtheselines, |     |     |
| ------- | --- | --- | --- | ---------------------------------- | --- | --- | --- | --- | ---------------- | --- | --- |
2× Tprec(SP,VL)×Tsens(SL,VP)
Tprec(SP,VL)+Tsens(SL,VP) Diceorcross-entropycanonlyguaranteehomotopyequiv-
|     |     |     |     | alenceifeverysinglevoxelissegmentedcorrectly. |     |     |     |     |     |     | Onthe |
| --- | --- | --- | --- | --------------------------------------------- | --- | --- | --- | --- | --- | --- | ----- |
Output:clDice
otherhand,clDicecanguaranteehomotopyequivalencefor
Figure4. Algorithm1calculatestheproposedsoft-skeleton,here a broader combinations of connected-voxels. Intuitively,
I isthemasktobesoft-skeletonizedandkisthenumberofitera- this is a very much desirable property as it makes clDice
tionsforskeletonization. Algorithm2,calculatesthesoft-clDice robusttowardsoutliersandnoisysegmentationlabels.
| loss,whereV | isareal-valuedprobabilisticpredictionfromaseg- |     |     |     |     |     |     |     |     |     |     |
| ----------- | ---------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
P
| mentationnetworkandV |     | isthetruemask.WedenoteHadamard |     |                  |     |     |     |     |     |     |     |
| -------------------- | --- | ------------------------------ | --- | ---------------- | --- | --- | --- | --- | --- | --- | --- |
|                      | L   |                                |     | 4.2.CostFunction |     |     |     |     |     |     |     |
productusing◦.
|     |     |     |     | Since | our objective |     | here is | to preserve |     | topology | while |
| --- | --- | --- | --- | ----- | ------------- | --- | ------- | ----------- | --- | -------- | ----- |
k =5...25inourexperiments,matchingthepixelradiusof
achievingaccuratesegmentations,andnottolearnskeleta,
the largest observed tubular structures. Choosing a larger wecombineourproposedsoft-clDicewithsoft-Diceinthe
| k does not | reduce performance | but increases | computation |     |     |     |     |     |     |     |     |
| ---------- | ------------------ | ------------- | ----------- | --- | --- | --- | --- | --- | --- | --- | --- |
followingmanner:
| time. On         | the other hand, | a too low k | leads to incomplete |     |                                    |     |     |     |     |     |     |
| ---------------- | --------------- | ----------- | ------------------- | --- | ---------------------------------- | --- | --- | --- | --- | --- | --- |
| skeletonization. |                 |             |                     | L   | =(1−α)(1−softDice)+α(1−softclDice) |     |     |     |     |     | (3) |
c
| In Figure | 3, the successive | steps of | our skeletonization |     |     |     |     |     |     |     |     |
| --------- | ----------------- | -------- | ------------------- | --- | --- | --- | --- | --- | --- | --- | --- |
areintuitivelyrepresented. Intheearlyiterations,thestruc- where α ∈ [0,0.5]. In stark contrast to previous works,
tureswithasmallradiusareskeletonizedandpreservedun- where segmentation and centerline prediction has been
til the later iterations when the thicker structures become learned jointly as multi-task learning [52, 49], we are not

interested in learning the centerline. We are interested in 5.3.ResultsandDiscussion
| learning | a topology-preserving |     |     | segmentation. |     | Therefore, |     |     |     |     |     |     |     |     |
| -------- | --------------------- | --- | --- | ------------- | --- | ---------- | --- | --- | --- | --- | --- | --- | --- | --- |
Wetrainedtwosegmentationarchitectures,aU-Netand
werestrictourexperimentalchoiceofalphatoα∈[0,0.5].
anFCN,forthevariouslossfunctionsinourexperimental
| We test | clDice | on two | state-of-the-art |     | network | architec- |     |     |     |     |     |     |     |     |
| ------- | ------ | ------ | ---------------- | --- | ------- | --------- | --- | --- | --- | --- | --- | --- | --- | --- |
tures: i) a 2D and 3D U-Net[39, 6], and ii) a 2D and 3D setup.Asabaseline,wetrainedthenetworksusingsoft-dice
|                                     |     |     |     |     |                |     | and compared | it  | with the | ones | trained | using | the proposed |     |
| ----------------------------------- | --- | --- | --- | --- | -------------- | --- | ------------ | --- | -------- | ---- | ------- | ----- | ------------ | --- |
| fullyconnectednetworks(FCN)[49,13]. |     |     |     |     | Asbaselines,we |     |              |     |          |      |         |       |              |     |
loss(Eq.3),byvaryingαfrom(0.1to0.5).
usethesamearchitecturestrainedusingsoft-Dice[27,47].
|     |     |     |     |     |     |     | Quantitative: | Weobservethatincludingsoft-clDiceinany |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ------------- | -------------------------------------- | --- | --- | --- | --- | --- | --- |
4.3.AdaptionforHighlyImbalancedData
|     |     |     |     |     |     |     | proportion | (α > | 0) leads | to improved |     | topological, |     | volu- |
| --- | --- | --- | --- | --- | --- | --- | ---------- | ---- | -------- | ----------- | --- | ------------ | --- | ----- |
Our theory (Section 3), describes a two-class problem metricandgraphsimilarityforall2Dand3Ddatasets,see
where clDice should be computed on both the foreground Table 1. We conclude that α can be interpreted as a hy-
andthebackgroundchannels. Inourexperiments,weshow per-dataset.
|     |     |     |     |     |     |     | per parameter | which | can | be tuned |     |     | Intuitively, |     |
| --- | --- | --- | --- | --- | --- | --- | ------------- | ----- | --- | -------- | --- | --- | ------------ | --- |
that for complex and highly imbalanced dataset it is suffi- increasingtheαimprovestheclDicemeasureformostex-
cient to calculate the clDice loss on the underrepresented periments. Most often, clDice is high or highest when the
| foregroundclass. |     | Weattributethistothedistinctproperties |     |     |     |     |     |     |     |     |     |     |     |     |
| ---------------- | --- | -------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
graphandtopologybasedmeasuresarehighorhighest,par-
oftubularness,sparsityofforegroundandthelackofcavi- ticularly the β Error, Streetmover distance and Opt-J F1
1
ties(Bettinumber2)inourdata. Anintuitiveinterpretation score; quantitatively indicating that topological properties
howtheseassumptionsarevalidintermsofdigitaltopology areindeedrepresentedintheclDicemeasure.
canbefoundinthesupplementarymaterial.
|     |     |     |     |     |     |     | In spite       | of not | optimizing |        | for a        | high soft-clDice |          | on  |
| --- | --- | --- | --- | --- | --- | --- | -------------- | ------ | ---------- | ------ | ------------ | ---------------- | -------- | --- |
|     |     |     |     |     |     |     | the background |        | class,     | all of | our networks |                  | converge | to  |
5.Experiments
|     |     |     |     |     |     |     | superior | segmentation | results. |     | This | not only | reinforces |     |
| --- | --- | --- | --- | --- | --- | --- | -------- | ------------ | -------- | --- | ---- | -------- | ---------- | --- |
5.1.Datasets our assumptions on dataset-specific necessary conditions
|     |     |     |     |     |     |     | but also | validates | the practical |     | applicability |     | of our | loss. |
| --- | --- | --- | --- | --- | --- | --- | -------- | --------- | ------------- | --- | ------------- | --- | ------ | ----- |
WeemployfivepublicdatasetsforvalidatingclDiceand
|     |     |     |     |     |     |     | Our findings | hold | for the | different | network |     | architectures, |     |
| --- | --- | --- | --- | --- | --- | --- | ------------ | ---- | ------- | --------- | ------- | --- | -------------- | --- |
soft-clDiceasameasureandanobjectivefunction,respec-
|     |     |     |     |     |     |     | for 2D | or 3D, | and for | tubular | or curvilinear |     | structures, |     |
| --- | --- | --- | --- | --- | --- | --- | ------ | ------ | ------- | ------- | -------------- | --- | ----------- | --- |
tively. In 2D, we evaluate on the DRIVE retina dataset strongly indicating its generalizability to analogous binary
[45],theMassachusettsRoadsdataset[28]andtheCREMI
segmentationtasks.
| neuron dataset                |          | [12]. In   | 3D, a   | synthetic            | vessel     | dataset with |                    |           |           |               |           |              |              |         |
| ----------------------------- | -------- | ---------- | ------- | -------------------- | ---------- | ------------ | ------------------ | --------- | --------- | ------------- | --------- | ------------ | ------------ | ------- |
| an added                      | Gaussian | noise      | term    | [41] and             | the Vessap | dataset      |                    |           |           |               |           |              |              |         |
|                               |          |            |         |                      |            |              | Observe            | that      | CREMI     | and the       | synthetic |              | vessel       | dataset |
| of multi-channel              |          | volumetric | scans   | of brain             | vessels    | is used      |                    |           |           |               |           |              |              |         |
|                               |          |            |         |                      |            |              | (see Supplementary |           | material) | appear        |           | to have      | the smallest |         |
| [50, 35].                     | For      | the Vessap | dataset | we train             | different  | mod-         |                    |           |           |               |           |              |              |         |
|                               |          |            |         |                      |            |              | increase           | in scores | over      | the baseline. |           | We attribute |              | this to |
| elsforoneandtwoinputchannels. |          |            |         | Forallofthedatasets, |            |              |                    |           |           |               |           |              |              |         |
thembeingtheleastcomplexdatasetsinthecollection,with
weperformthreefoldcross-validationandtestonheld-out,
|            |                |     |      |               |            |     | CREMI         | having | an almost | uniform | thickness       |     | of radii | and |
| ---------- | -------------- | --- | ---- | ------------- | ---------- | --- | ------------- | ------ | --------- | ------- | --------------- | --- | -------- | --- |
| large, and | highly-variant |     | test | sets. Details | concerning | the |               |        |           |         |                 |     |          |     |
|            |                |     |      |               |            |     | the synthetic | data   | having    | a high  | signal-to-noise |     | ratio    | and |
experimentalsetupcanbefoundinthesupplementary.
|     |     |     |     |     |     |     | insignificant | illumination |     | variation. | More | importantly, |     | we  |
| --- | --- | --- | --- | --- | --- | --- | ------------- | ------------ | --- | ---------- | ---- | ------------ | --- | --- |
5.2.EvaluationMetrics observelargerimprovementsforallmeasuresincaseofthe
morecomplexVessapandRoadsdataseeFigure5.Indirect
We compare the performance of various experimental comparisontoperformancemeasuresreportedintworecent
| setups using | three | types | of metrics: | volumetric, |     | topology- |                       |     |     |                  |     |     |          |     |
| ------------ | ----- | ----- | ----------- | ----------- | --- | --------- | --------------------- | --- | --- | ---------------- | --- | --- | -------- | --- |
|              |       |       |             |             |     |           | publicationsbyHuetal. |     |     | andMosinskaetal. |     |     | [17,29], | we  |
based,andgraph-based.
findthatourapproachisonparorbetterintermsofAccu-
1. Volumetric: We compute volumetric scores such as racyandBettiErrorfortheRoadsandCREMIdataset. Itis
Dicecoefficient,Accuracy,andtheproposedclDice. importanttonotethatweusedasmallersubsetoftraining
datafortheRoaddatasetcomparedtobothwhileusingthe
| 2. Topology-based:                       |        |         | We calculate | the     | mean  | of absolute |              |              |     |       |           |     |       |       |
| ---------------------------------------- | ------ | ------- | ------------ | ------- | ----- | ----------- | ------------ | ------------ | --- | ----- | --------- | --- | ----- | ----- |
| Betti                                    | Errors | for the | Betti        | Numbers | β and | β and the   | sametestset. |              |     |       |           |     |       |       |
|                                          |        |         |              |         | 0     | 1           |              |              |     |       |           |     |       |       |
| meanabsoluteerrorofEulercharacteristic,χ |        |         |              |         |       | = V −       |              |              |     |       |           |     |       |       |
|                                          |        |         |              |         |       |             | Hu et        | al. reported | a   | Betti | error for | the | DRIVE | data, |
E+F,whereV,E, andF denotesnumberofvertices, which exceeds ours; however, it is important to consider
edges,andfaces. thattheirapproachexplicitlyminimizesthemismatchofthe
3. Graph-based:weextractrandompatch-wisegraphsfor persistence diagram, which has significantly higher com-
the 2D/3D images. We uniformly sample fixed num- putational complexity during training, see the section be-
ber of points from the graph and compute the Street- low. We find that our proposed loss performs superior to
moverDistance (SMD) [4]. SMD captures a Wasser- thebaselineinalmosteveryscenario.Theimprovementap-
stein distance between two graphs. Additionally we pearstobepronouncedwhenevaluatingthehighlyrelevant
computetheF1scoreofjunction-basedmetric[7]. graphandtopologybasedmeasures,includingtherecently

Table1. QuantitativeexperimentalresultsfortheMassachusettsroaddataset(Roads),theCREMIdataset,theDRIVEretinadatasetand
theVessapdataset(3D).Boldnumbersindicatethebestperformance. TheperformanceaccordingtotheclDicemeasureishighlightedin
rose. Forallexperimentsweobservethatusingsoft-clDiceinL c resultsinimprovedscorescomparedtosoft-Dice. Thisimprovement
holdsforalmostα>0;αcanbeinterpretedasadatasetspecifichyper-parameter.
Dataset Network Loss Dice Accuracy clDice β0Error β1Error SMD[4] χerror Opt-JF1[7]
|     |     | soft-dice | 64.84 95.16 | 70.79 | 1.474 1.408 0.1216 | 2.634 | 0.766 |
| --- | --- | --------- | ----------- | ----- | ------------------ | ----- | ----- |
FCN
|     |     | Lc,α=0.1 | 66.52 95.70 | 74.80 | 0.987 1.227 0.1002 | 2.625 | 0.768 |
| --- | --- | -------- | ----------- | ----- | ------------------ | ----- | ----- |
|     |     | Lc,α=0.2 | 67.42 95.80 | 76.25 | 0.920 1.280 0.0954 | 2.526 | 0.770 |
|     |     | Lc,α=0.3 | 65.90 95.35 | 74.86 | 0.974 1.197 0.1003 | 2.448 | 0.775 |
|     |     | Lc,α=0.4 | 67.18 95.46 | 76.92 | 0.934 1.092 0.0991 | 2.183 | 0.803 |
|     |     | Lc,α=0.5 | 65.77 95.09 | 75.22 | 0.947 1.184 0.0991 | 2.361 | 0.782 |
Roads soft-dice 76.23 96.75 86.83 0.491 1.256 0.0589 1.120 0.881
|     |     | Lc,α=0.1 | 76.66 96.77 | 87.35 | 0.359 0.938 0.0457 | 0.980 | 0.878 |
| --- | --- | -------- | ----------- | ----- | ------------------ | ----- | ----- |
|     |     | Lc,α=0.2 | 76.25 96.76 | 87.29 | 0.312 1.031 0.0415 | 0.865 | 0.900 |
U-NET
|     |               | Lc,α=0.3  | 74.85 96.57 | 86.10 | 0.322 1.062 0.0504 | 0.827 | 0.913 |
| --- | ------------- | --------- | ----------- | ----- | ------------------ | ----- | ----- |
|     |               | Lc,α=0.4  | 75.38 96.60 | 86.16 | 0.344 1.016 0.0483 | 0.755 | 0.916 |
|     |               | Lc,α=0.5  | 76.45 96.64 | 88.17 | 0.375 0.953 0.0527 | 1.080 | 0.894 |
|     | Mosinskaetal. | [29,17]   | - 97.54     | -     | - 2.781            | - -   | -     |
|     | Huetal.       | [17]      | - 97.28     | -     | - 1.275            | - -   | -     |
|     |               | soft-dice | 91.54 97.11 | 95.86 | 0.259 0.657 0.0461 | 1.087 | 0.904 |
|     |               | Lc,α=0.1  | 91.76 97.21 | 96.05 | 0.222 0.556 0.0395 | 1.000 | 0.900 |
|     |               | Lc,α=0.2  | 91.66 97.15 | 96.01 | 0.231 0.630 0.0419 | 0.991 | 0.902 |
U-NET
|     |     | Lc,α=0.3 | 91.78 97.18 | 96.21 | 0.204 0.537 0.0437 | 0.919 | 0.913 |
| --- | --- | -------- | ----------- | ----- | ------------------ | ----- | ----- |
CREMI Lc,α=0.4 91.56 97.12 96.09 0.250 0.630 0.0444 0.995 0.902
|     |               | Lc,α=0.5  | 91.66 97.16 | 96.16 | 0.231 0.620 0.0455 | 0.991 | 0.907 |
| --- | ------------- | --------- | ----------- | ----- | ------------------ | ----- | ----- |
|     | Mosinskaetal. | [29,17]   | 82.30 94.67 | -     | - 1.973            | - -   | -     |
|     | Huetal.       | [17]      | - 94.56     | -     | - 1.113            | - -   | -     |
|     |               | soft-Dice | 78.23 96.27 | 78.02 | 2.187 1.860 0.0429 | 3.275 | 0.773 |
Lc,α=0.1
|     |     |          | 78.36 96.25 | 79.02 | 2.100 1.610 0.0393 | 3.203 | 0.777 |
| --- | --- | -------- | ----------- | ----- | ------------------ | ----- | ----- |
|     |     | Lc,α=0.2 | 78.75 96.29 | 80.22 | 1.892 1.382 0.0383 | 2.895 | 0.793 |
FCN
|     |     | Lc,α=0.3 | 78.29 96.20 | 80.28 | 1.888 1.332 0.0318 | 2.918 | 0.798 |
| --- | --- | -------- | ----------- | ----- | ------------------ | ----- | ----- |
|     |     | Lc,α=0.4 | 78.00 96.11 | 80.43 | 2.036 1.602 0.0423 | 3.141 | 0.764 |
DRIVEretina
|     |     | Lc,α=0.5  | 77.76 96.04 | 80.95 | 1.836 1.408 0.0394 | 2.848 | 0.794 |
| --- | --- | --------- | ----------- | ----- | ------------------ | ----- | ----- |
|     |     | soft-Dice | 74.25 95.63 | 75.71 | 1.745 1.455 0.0649 | 2.997 | 0.760 |
U-Net
|     |               | Lc,α=0.5  | 75.21 95.82 | 76.86 | 1.538 1.389 0.0586  | 2.737 | 0.767 |
| --- | ------------- | --------- | ----------- | ----- | ------------------- | ----- | ----- |
|     | Mosinskaetal. | [29,17]   | - 95.43     | -     | - 2.784             | - -   | -     |
|     | Huetal.       | [17]      | - 95.21     | -     | - 1.076             | - -   | -     |
|     |               | soft-dice | 85.21 96.03 | 90.88 | 3.385 4.458 0.00459 | 5.850 | 0.862 |
FCN,1ch
|     |     | Lc,α=0.5  | 85.44 95.91 | 91.32 | 2.292 3.677 0.00417 | 5.620 | 0.864 |
| --- | --- | --------- | ----------- | ----- | ------------------- | ----- | ----- |
|     |     | soft-dice | 85.31 95.82 | 90.10 | 2.833 4.771 0.00629 | 6.080 | 0.849 |
|     |     | Lc,α=0.1  | 85.96 95.99 | 91.02 | 2.896 4.156 0.00447 | 5.980 | 0.860 |
|     |     | Lc,α=0.2  | 86.45 96.11 | 91.22 | 2.656 4.385 0.00466 | 5.530 | 0.869 |
FCN,2ch
|     |     | Lc,α=0.3 | 85.72 95.93 | 91.20 | 2.719 4.469 0.00423 | 5.470 | 0.866 |
| --- | --- | -------- | ----------- | ----- | ------------------- | ----- | ----- |
|     |     | Lc,α=0.4 | 85.65 95.95 | 91.65 | 2.719 4.469 0.00423 | 5.670 | 0.869 |
|     |     | Lc,α=0.5 | 85.28 95.76 | 91.22 | 2.615 4.615 0.00433 | 5.320 | 0.870 |
Vessapdata
|     |     | soft-dice | 87.46 96.35 | 91.18 | 3.094 5.042 0.00549 | 5.300 | 0.863 |
| --- | --- | --------- | ----------- | ----- | ------------------- | ----- | ----- |
U-Net,1ch
|     |     | Lc,α=0.5  | 87.82 96.52 | 93.03 | 2.656 4.615 0.00533 | 4.910 | 0.872 |
| --- | --- | --------- | ----------- | ----- | ------------------- | ----- | ----- |
|     |     | soft-dice | 87.98 96.56 | 90.16 | 2.344 4.323 0.00507 | 5.550 | 0.855 |
|     |     | Lc,α=0.1  | 88.13 96.59 | 91.12 | 2.302 4.490 0.00465 | 5.180 | 0.872 |
|     |     | Lc,α=0.2  | 87.96 96.74 | 92.52 | 2.208 3.979 0.00342 | 4.830 | 0.861 |
U-Net,2ch
|     |     | Lc,α=0.3 | 87.70 96.71 | 92.56 | 2.115 4.521 0.00309 | 5.260 | 0.858 |
| --- | --- | -------- | ----------- | ----- | ------------------- | ----- | ----- |
|     |     | Lc,α=0.4 | 88.57 96.87 | 93.25 | 2.281 4.302 0.00327 | 5.370 | 0.868 |
Lc,α=0.5
|     |     |     | 88.14 96.74 | 92.75 | 2.135 4.125 0.00328 | 5.390 | 0.864 |
| --- | --- | --- | ----------- | ----- | ------------------- | ----- | ----- |
introduced OPT-Junction F1 by Citraro et al. [7]. Our re- DRIVEdataset. FortheCREMIdataset, weobservethese
sults are consistent across different network architectures, situationslessfrequently,whichisinlinewiththeveryhigh
indicatingthatsoft-clDicecanbedeployedtoanynetwork quantitative scores on the CREMI data. Interestingly, in
architecture. thereal3Dvesseldataset, thesoft-Dicelossoversegments
|              |           |                    |                  | vessels, | leading to false positive | connections. | This is not |
| ------------ | --------- | ------------------ | ---------------- | -------- | ------------------------- | ------------ | ----------- |
| Qualitative: | In Figure | 5, typical results | for our datasets |          |                           |              |             |
are depicted. Our networks trained on the proposed loss the case when using our proposed loss function, which
|     |     |     |     | we attribute | to its topology-preserving | nature. | Additional |
| --- | --- | --- | --- | ------------ | -------------------------- | ------- | ---------- |
termrecoverconnections,whichwerefalsenegativeswhen
trained with the soft-Dice loss. These missed connections qualitativeresultscanbeinspectedinthesupplementary.
| appear to | be particularly | frequent in the | complex road and |     |     |     |     |
| --------- | --------------- | --------------- | ---------------- | --- | --- | --- | --- |

|                                       |           |             |              |              |            |                |        | Image | Label | Soft-Dice |     | Ours |
| ------------------------------------- | --------- | ----------- | ------------ | ------------ | ---------- | -------------- | ------ | ----- | ----- | --------- | --- | ---- |
| Computational                         |           | Efficiency: |              | Naturally,   | inference  |                | times  |       |       |           |     |      |
| of CNNs                               | with      | the same    | architecture |              | but        | different      | train- |       |       |           |     |      |
| ing losses                            | are       | identical.  | However,     |              | during     | training,      | our    |       |       |           |     |      |
| soft-skeleton                         | algorithm |             | requires     | O(kn2)       | complexity |                | for    |       |       |           |     |      |
| an n ×                                | n 2D      | image where | k            | is the       | number     | of iterations. |        |       |       |           |     |      |
| As a comparison,                      |           | [17]        | needs        | O(c2mlog(m)) |            | (see           | [15])  |       |       |           |     |      |
| complexity                            | to        | compute     | the 1d       | persistent   | homology   |                | where  |       |       |           |     |      |
| d is the                              | number    | of          | points       | with zero    | gradients  |                | in the |       |       |           |     |      |
| predictionandmisthenumberofsimplices. |           |             |              |              |            | Roughly,cis    |        |       |       |           |     |      |
| proportional                          | to        | n2, and     | m is         | of O(n2)     | for a      | 2D Euclidean   |        |       |       |           |     |      |
O(n6log(n)).
| grid. Thus,   | the   | worst    | complexity | of       | [17] is       |     |      |     |     |     |     |     |
| ------------- | ----- | -------- | ---------- | -------- | ------------- | --- | ---- | --- | --- | --- | --- | --- |
| Additionally, | their | approach |            | requires | an O(clog(c)) |     | com- |     |     |     |     |     |
plexitytofindanoptimalmatchingofthebirth-deathpairs.
| We note       | that         | the total | run-time     | overhead |        | for soft-clDice |       |     |     |     |     |     |
| ------------- | ------------ | --------- | ------------ | -------- | ------ | --------------- | ----- | --- | --- | --- | --- | --- |
| compared      | to soft-Dice |           | is marginal, | i.e.,    | for    | batch-size      | of 4  |     |     |     |     |     |
| and 1024x1024 |              | image     | resolution,  | the      | former | takes           | 1.35s |     |     |     |     |     |
whilethelattertakes1.24sonaverage(<10%increase)on
anRTX-8000.
| Future          | Work:      | Although  | our           | proposed     | soft-skeleton   |                | ap-   |     |     |     |     |     |
| --------------- | ---------- | --------- | ------------- | ------------ | --------------- | -------------- | ----- | --- | --- | --- | --- | --- |
| proximation     | works      | well      | in practice,  |              | a better        | differentiable |       |     |     |     |     |     |
| skeletonization |            | can only  | improve       | performance, |                 | which          | we    |     |     |     |     |     |
| reserve         | for future | research. |               | Any such     | skeletonization |                | can   |     |     |     |     |     |
| be readily      | plugged    | into      | our approach. |              | Furthermore,    |                | theo- |     |     |     |     |     |
reticalandexperimentalmulti-classstudieswouldsensibly
extendourstudy.
6.ConclusiveRemarks
| We           | introduce                                | clDice,          | a              | novel     | topology-preserving |               |         |     |     |     |     |     |
| ------------ | ---------------------------------------- | ---------------- | -------------- | --------- | ------------------- | ------------- | ------- | --- | --- | --- | --- | --- |
| similarity   | measure                                  | for              | tubular        | structure |                     | segmentation. |         |     |     |     |     |     |
| Importantly, | wepresentatheoreticalguaranteethatclDice |                  |                |           |                     |               |         |     |     |     |     |     |
| enforces     | topology                                 | preservation     |                | up        | to homotopy         |               | equiva- |     |     |     |     |     |
| lence. Next, | we                                       | use a            | differentiable |           | version             | of the        | clDice, |     |     |     |     |     |
| soft-clDice, | in                                       | a loss function, |                | to train  | state-of-the-art    |               | 2D      |     |     |     |     |     |
clDice
| and 3D               | neural        | networks.     | We                              | use                   |              | to benchmark |      |     |     |     |     |     |
| -------------------- | ------------- | ------------- | ------------------------------- | --------------------- | ------------ | ------------ | ---- | --- | --- | --- | --- | --- |
| segmentation         |               | quality       | from                            | a topology-preserving |              |              | per- |     |     |     |     |     |
| spective             | along         | with multiple |                                 | volumetric,           | topological, |              | and  |     |     |     |     |     |
| graph-basedmeasures. |               |               | Wefindthattrainingonsoft-clDice |                       |              |              |      |     |     |     |     |     |
| leads to             | segmentations |               | with                            | more                  | accurate     | connectivity |      |     |     |     |     |     |
information,bettergraph-similarity,betterEulercharacter-
| istics, and | improved | Dice | and | Accuracy. | Our | soft-clDice |     |     |     |     |     |     |
| ----------- | -------- | ---- | --- | --------- | --- | ----------- | --- | --- | --- | --- | --- | --- |
Figure5.Qualitativeresults:fromtoptobottomweshowtworows
| is computationally |     | efficient |     | and can | be readily | deployed |     |               |                              |     |                |     |
| ------------------ | --- | --------- | --- | ------- | ---------- | -------- | --- | ------------- | ---------------------------- | --- | -------------- | --- |
|                    |     |           |     |         |            |          |     | ofresultsfor: | theMassachusettsroaddataset, |     | theDRIVEretina |     |
to any other deep learning-based segmentation tasks such dataset,theCREMIneurondataand2Dslicesfromthe3DVessap
as neuron segmentation in biomedical imaging, crack dataset. From left to right, the real image, the label, the predic-
detectioninindustrialqualitycontrol,orremotesensing. tionusingsoft-DiceandtheU-NetpredictionsusingL (α=0.5)
c
areshown,respectively.TheimagesindicatethatclDicesegments
Acknowledgement: J.C.Paetzold. andS.Shit. aresup- road,retinavesselconnectionsandneuronconnectionswhichthe
soft-Dicelossmisses,butalsodoesnotsegmentfalse-positiveves-
| ported by  | the | GCB and   | Translatum, |           | TU Munich. |        | S.Shit., |             |                    |                    |     |               |
| ---------- | --- | --------- | ----------- | --------- | ---------- | ------ | -------- | ----------- | ------------------ | ------------------ | --- | ------------- |
|            |     |           |             |           |            |        |          | sels in 3D. | Some, but not all, | missed connections |     | are indicated |
| A. Zhylka. | and | I. Ezhov. | are         | supported | by         | TRABIT | (EU      |             |                    |                    |     |               |
withsolidredarrows,falsepositivesareindicatedwithred-yellow
| Grant: 765148). |     | We thank | Ali | Ertuerk, | Mihail | I. Todorov, |     |                                                         |     |     |     |     |
| --------------- | --- | -------- | --- | -------- | ------ | ----------- | --- | ------------------------------------------------------- | --- | --- | --- | --- |
|                 |     |          |     |          |        |             |     | arrows. MorequalitativeresultscanbefoundintheSupplemen- |     |     |     |     |
NilsBo¨rnerandGilesTetteh.
tarymaterial.

References [16] Kai Hu et al. Retinal vessel segmentation of color fundus
|     |     |     |     |     |     |     | images | using | multiscale |     | convolutional | neural | network | with |
| --- | --- | --- | --- | --- | --- | --- | ------ | ----- | ---------- | --- | ------------- | ------ | ------- | ---- |
[1] Pavel S Aleksandrov. Combinatorial topology, volume 1. animprovedcross-entropylossfunction. Neurocomputing,
| CourierCorporation,1998. |              |                                    | 4              |            |     |       |                                                          |                                |     |     |     |     |         |     |
| ------------------------ | ------------ | ---------------------------------- | -------------- | ---------- | --- | ----- | -------------------------------------------------------- | ------------------------------ | --- | --- | --- | --- | ------- | --- |
|                          |              |                                    |                |            |     |       | 309:179–191,2018.                                        |                                |     | 1   |     |     |         |     |
| [2] BjoernAndresetal.    |              | Probabilisticimagesegmentationwith |                |            |     |       |                                                          |                                |     |     |     |     |         |     |
|                          |              |                                    |                |            |     |       | [17] XiaolingHuetal.Topology-preservingdeepimagesegmen-  |                                |     |     |     |     |         |     |
| closedness               | constraints. |                                    | In ICCV, pages | 2611–2618. |     | IEEE, |                                                          |                                |     |     |     |     |         |     |
|                          |              |                                    |                |            |     |       | tation.                                                  | InNeurIPS,pages5658–5669,2019. |     |     |     |     | 2,6,7,8 |     |
| 2011.                    | 2            |                                    |                |            |     |       |                                                          |                                |     |     |     |     |         |     |
|                          |              |                                    |                |            |     |       | [18] JesseMHunteretal.Morphologicalandpathologicalevolu- |                                |     |     |     |     |         |     |
[3] RicardoJArau´jo,JaimeSCardoso,andHe´lderPOliveira.
tionofthebrainmicrocirculationinagingandAlzheimer’s
Adeeplearningdesignforimprovingtopologycoherencein
|     |     |     |     |     |     |     | disease. |     | PloSone,7(5):e36893,2012. |     |     | 1   |     |     |
| --- | --- | --- | --- | --- | --- | --- | -------- | --- | ------------------------- | --- | --- | --- | --- | --- |
InInternationalConferenceon
bloodvesselsegmentation.
|     |     |     |     |     |     |     | [19] DakaiJin,ZiyueXu,AdamPHarrison,KevinGeorge,and |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
MedicalImageComputingandComputer-AssistedInterven-
|                                 |     |     |     |     |     |     | Daniel | J   | Mollura. | 3d convolutional |     | neural | networks | with |
| ------------------------------- | --- | --- | --- | --- | --- | --- | ------ | --- | -------- | ---------------- | --- | ------ | -------- | ---- |
| tion,pages93–101.Springer,2019. |     |     |     | 2   |     |     |        |     |          |                  |     |        |          |      |
graphrefinementforairwaysegmentationusingincomplete
| [4] Davide | Belli and | Thomas | Kipf. Image-conditioned |     |     | graph |     |     |     |     |     |     |     |     |
| ---------- | --------- | ------ | ----------------------- | --- | --- | ----- | --- | --- | --- | --- | --- | --- | --- | --- |
datalabels.InInternationalWorkshoponMachineLearning
generation for road network extraction. arXiv preprint inMedicalImaging,pages141–149.Springer,2017. 2
| arXiv:1910.14388,2019. |          |             | 6,7,16    |     |          |       |                                                            |     |     |     |     |     |     |     |
| ---------------------- | -------- | ----------- | --------- | --- | -------- | ----- | ---------------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
|                        |          |             |           |     |          |       | [20] AnneJouteletal.Cerebrovasculardysfunctionandmicrocir- |     |     |     |     |     |     |     |
| [5] A¨ıcha             | BenTaieb | and Ghassan | Hamarneh. |     | Topology | aware |                                                            |     |     |     |     |     |     |     |
culationrarefactionprecedewhitematterlesionsinamouse
fullyconvolutionalnetworksforhistologyglandsegmenta-
geneticmodelofcerebralischemicsmallvesseldisease.JCI,
| tion.                       | InMICCAI,pages460–468.Springer,2016. |          |                    |          | 2          |      |                                 |     |     |     |                         |                        |     |     |
| --------------------------- | ------------------------------------ | -------- | ------------------ | -------- | ---------- | ---- | ------------------------------- | --- | --- | --- | ----------------------- | ---------------------- | --- | --- |
|                             |                                      |          |                    |          |            |      | 120(2):433–445,2010.            |     |     | 1   |                         |                        |     |     |
| [6] O¨zgu¨n                 | C¸ic¸ek and                          | Aothers. | 3D U-Net:          | learning | dense      | vol- |                                 |     |     |     |                         |                        |     |     |
|                             |                                      |          |                    |          |            |      | [21] CemilKirbasandFrancisQuek. |     |     |     |                         | Areviewofvesselextrac- |     |     |
| umetric                     | segmentation                         | from     | sparse annotation. |          | In MICCAI, |      |                                 |     |     |     |                         |                        |     |     |
|                             |                                      |          |                    |          |            |      | tiontechniquesandalgorithms.    |     |     |     | CSUR,36(2):81–121,2004. |                        |     |     |
| pages424–432.Springer,2016. |                                      |          | 6                  |          |            |      |                                 |     |     |     |                         |                        |     |     |
1
| [7] Leonardo | Citraro, | Mateusz | Kozin´ski, | and | Pascal Fua. | To- |          |       |           |        |      |        |           |      |
| ------------ | -------- | ------- | ---------- | --- | ----------- | --- | -------- | ----- | --------- | ------ | ---- | ------ | --------- | ---- |
|              |          |         |            |     |             |     | [22] Bin | Kong, | Xin Wang, | Junjie | Bai, | Yi Lu, | Feng Gao, | Kun- |
wardsreliableevaluationofalgorithmsforroadnetworkre-
|     |     |     |     |     |     |     | lin | Cao, | Jun Xia, | Qi Song, | and | Youbing | Yin. | Learning |
| --- | --- | --- | --- | --- | --- | --- | --- | ---- | -------- | -------- | --- | ------- | ---- | -------- |
constructionfromaerialimages.InEuropeanConferenceon
|                                            |                  |           |              |        |            |     | tree-structured |      | representation |          | for          | 3d coronary | artery | seg-      |
| ------------------------------------------ | ---------------- | --------- | ------------ | ------ | ---------- | --- | --------------- | ---- | -------------- | -------- | ------------ | ----------- | ------ | --------- |
| ComputerVision,pages703–719.Springer,2020. |                  |           |              |        | 6,7,16     |     |                 |      |                |          |              |             |        |           |
|                                            |                  |           |              |        |            |     | mentation.      |      | Computerized   |          | Medical      | Imaging     | and    | Graphics, |
| [8] James                                  | Clough, Nicholas |           | Byrne, Ilkay | Oksuz, | Veronika   | A   |                 |      |                |          |              |             |        |           |
|                                            |                  |           |              |        |            |     | 80:101688,2020. |      |                | 2        |              |             |        |           |
| Zimmer,                                    | Julia A          | Schnabel, | and Andrew   | King.  | A topolog- |     |                 |      |                |          |              |             |        |           |
|                                            |                  |           |              |        |            |     | [23] T.         | Yung | Kong. On       | topology | preservation |             | in 2-D | and 3-D   |
icallossfunctionfordeep-learningbasedimagesegmenta-
|     |     |     |     |     |     |     | thinning. |     | International |     | journal | of pattern | recognition | and |
| --- | --- | --- | --- | --- | --- | --- | --------- | --- | ------------- | --- | ------- | ---------- | ----------- | --- |
IEEETransactionsonPat-
tionusingpersistenthomology.
|                                          |     |     |                        |     |     |     | artificialintelligence,9(05):813–844,1995. |     |     |                                  |     |                        | 2,3,4,11,12 |     |
| ---------------------------------------- | --- | --- | ---------------------- | --- | --- | --- | ------------------------------------------ | --- | --- | -------------------------------- | --- | ---------------------- | ----------- | --- |
| ternAnalysisandMachineIntelligence,2020. |     |     |                        |     | 2   |     |                                            |     |     |                                  |     |                        |             |     |
|                                          |     |     |                        |     |     |     | [24] TYungKongandAzrielRosenfeld.          |     |     |                                  |     | Digitaltopology:Intro- |             |     |
| [9] AntoninoPaoloDiGiovannaetal.         |     |     | Whole-brainvasculature |     |     |     |                                            |     |     |                                  |     |                        |             |     |
|                                          |     |     |                        |     |     |     | ductionandsurvey.                          |     |     | ComputerVision,Graphics,andImage |     |                        |             |     |
reconstructionatthesinglecapillarylevel.Scientificreports,
|                  |     |     |     |     |     |     | Processing,48(3):357–393,1989. |     |     |                                    |     | 3,4,12 |     |     |
| ---------------- | --- | --- | --- | --- | --- | --- | ------------------------------ | --- | --- | ---------------------------------- | --- | ------ | --- | --- |
| 8(1):12573,2018. |     | 2   |     |     |     |     |                                |     |     |                                    |     |        |     |     |
|                  |     |     |     |     |     |     | [25] Ta-ChihLeeetal.           |     |     | Buildingskeletonmodelsvia3-Dmedial |     |        |     |     |
[10] HerbertEdelsbrunneretal.Topologicalpersistenceandsim-
surfaceaxisthinningalgorithms.CVGIP:GraphicalModels
| plification.                          | InFOCS,pages454–463.IEEE,2000. |          |              |                     | 2     |       |                                              |     |     |                                     |     |     |     |     |
| ------------------------------------- | ------------------------------ | -------- | ------------ | ------------------- | ----- | ----- | -------------------------------------------- | --- | --- | ----------------------------------- | --- | --- | --- | --- |
|                                       |                                |          |              |                     |       |       | andImageProcessing,56(6):462–478,1994.       |     |     |                                     |     |     | 2   |     |
| [11] HerbertEdelsbrunnerandJohnHarer. |                                |          |              | Computationaltopol- |       |       |                                              |     |     |                                     |     |     |     |     |
|                                       |                                |          |              |                     |       |       | [26] CherngMinMa.                            |     |     | Ontopologypreservationin3Dthinning. |     |     |     |     |
| ogy:                                  | an introduction.               | American | Mathematical |                     | Soc., | 2010. |                                              |     |     |                                     |     |     |     |     |
|                                       |                                |          |              |                     |       |       | CVGIP:Imageunderstanding,59(3):328–339,1994. |     |     |                                     |     |     |     | 2   |
2
|                 |                |          |           |            |              |        | [27] FaustoMilletarietal.                   |     |     | V-net:Fullyconvolutionalneuralnet- |     |     |     |        |
| --------------- | -------------- | -------- | --------- | ---------- | ------------ | ------ | ------------------------------------------- | --- | --- | ---------------------------------- | --- | --- | --- | ------ |
| [12] Jan Funke, | Fabian         | Tschopp, | William   | Grisaitis, | Arlo         | Sheri- |                                             |     |     |                                    |     |     |     |        |
|                 |                |          |           |            |              |        | worksforvolumetricmedicalimagesegmentation. |     |     |                                    |     |     |     | In3DV, |
| dan,            | Chandan Singh, | Stephan  | Saalfeld, |            | and Srinivas | C.     |                                             |     |     |                                    |     |     |     |        |
|                 |                |          |           |            |              |        | pages565–571.IEEE,2016.                     |     |     |                                    | 6   |     |     |        |
Turaga.Largescaleimagesegmentationwithstructuredloss
based deep learning for connectome reconstruction. IEEE [28] VolodymyrMnih. MachineLearningforAerialImageLa-
TransactionsonPatternAnalysisandMachineIntelligence, beling. PhDthesis,UniversityofToronto,2013. 6
41(7):1669–1680,Jul2019. 6 [29] Agata Mosinska et al. Beyond the pixel-wise loss for
CVPR,
[13] StefanGerletal. Adistance-basedlossforsmoothandcon- topology-aware delineation. In pages 3136–3145,
| tinuousskinlayersegmentationinoptoacousticimages. |     |     |     |     |     | In  | 2018. | 2,6,7 |     |     |     |     |     |     |
| ------------------------------------------------- | --- | --- | --- | --- | --- | --- | ----- | ----- | --- | --- | --- | --- | --- | --- |
InternationalConferenceonMedicalImageComputingand [30] Agata Mosinska, Mateusz Kozin´ski, and Pascal Fua. Joint
Computer-Assisted Intervention, segmentation and path classification of curvilinear struc-
|       |     |     | pages | 309–319. | Springer, |     |        |                                             |     |     |     |     |     |     |
| ----- | --- | --- | ----- | -------- | --------- | --- | ------ | ------------------------------------------- | --- | --- | --- | --- | --- | --- |
| 2020. | 6   |     |       |          |           |     | tures. | IEEETransactionsonPatternAnalysisandMachine |     |     |     |     |     |     |
[14] ShirGur,LiorWolf,LiorGolgher,andPabloBlinder. Un- Intelligence,42(6):1515–1521,2019. 2
supervised microvascular image segmentation using an ac- [31] Fernando Navarro, Suprosanna Shit, et al. Shape-aware
tive contours mimicking neural network. In Proceedings complementary-task learning for multi-organ segmenta-
oftheIEEE/CVFInternationalConferenceonComputerVi- tion. InInternationalWorkshoponMLMI,pages620–627.
| sion,pages10722–10731,2019. |     |     | 2   |     |     |     | Springer,2019. |     | 2   |     |     |     |     |     |
| --------------------------- | --- | --- | --- | --- | --- | --- | -------------- | --- | --- | --- | --- | --- | --- | --- |
[15] Xiao Han et al. A topology preserving level set method [32] SebastianNowozinandChristophHLampert. Globalcon-
forgeometricdeformablemodels. IEEETPAMI,25(6):755– nectivitypotentialsforrandomfieldmodels.InCVPR,pages
| 768,2003. | 2,8 |     |     |     |     |     | 818–825.IEEE,2009. |     |     | 2   |     |     |     |     |
| --------- | --- | --- | --- | --- | --- | --- | ------------------ | --- | --- | --- | --- | --- | --- | --- |

[33] DorukOner,MateuszKozin´ski,LeonardoCitraro,NathanC [51] Engin Tu¨retken et al. Reconstructing curvilinear networks
Dadap, Alexandra G Konings, and Pascal Fua. Promoting using path classifiers and integer programming. IEEE
connectivity of network-like structures by enforcing region TPAMI,38(12):2515–2530,2016. 2
separation. arXivpreprintarXiv:2009.07011,2020. 14 [52] Fatmatu¨lzehra Uslu and Anil Anthony Bharath. A multi-
[34] Martin Ralf Oswald et al. Generalized connectivity con- task network to detect junctions in retinal vasculature. In
straints for spatio-temporal 3D reconstruction. In ECCV, MICCAI,pages92–100.Springer,2018. 5
| pages32–46.Springer,2014.                  |     |     |     | 2   |                |     |              |       |         |           |             |          |              |
| ------------------------------------------ | --- | --- | --- | --- | -------------- | --- | ------------ | ----- | ------- | --------- | ----------- | -------- | ------------ |
|                                            |     |     |     |     |                |     | [53] Subeesh | Vasu, | Mateusz | Kozinski, |             | Leonardo | Citraro, and |
| [35] JohannesCPaetzold,OliverSchoppe,etal. |     |     |     |     | Transferlearn- |     |              |       |         |           |             |          |              |
|                                            |     |     |     |     |                |     | Pascal       | Fua.  | Topoal: | An        | adversarial | learning | approach     |
ing from synthetic data reduces need for labels to segment for topology-aware road segmentation. arXiv preprint
brain vasculature and neural pathways in 3d. In Interna- arXiv:2007.09084,2020. 2
tionalConferenceonMedicalImagingwithDeepLearning–
[54] SaraVicenteetal.Graphcutbasedimagesegmentationwith
| ExtendedAbstractTrack,2019. |           |     |                  | 6   |          |           |                      |     |     |                                  |     |     |     |
| --------------------------- | --------- | --- | ---------------- | --- | -------- | --------- | -------------------- | --- | --- | -------------------------------- | --- | --- | --- |
|                             |           |     |                  |     |          |           | connectivitypriors.  |     |     | InCVPR,pages1–8.IEEE,2008.       |     |     | 2   |
| [36] Ka´lma´n               | Pala´gyi. |     | A 3-subiteration | 3D  | thinning | algorithm |                      |     |     |                                  |     |     |     |
|                             |           |     |                  |     |          |           | [55] JanDWegneretal. |     |     | Ahigher-orderCRFmodelforroadnet- |     |     |     |
forextractingmedialsurfaces. PatternRecognitionLetters, workextraction. InCVPR,pages1698–1705.IEEE,2013.
| 23(6):663–675,2002. |         |        | 2,4      |              |     |         | 2   |     |     |     |     |     |     |
| ------------------- | ------- | ------ | -------- | ------------ | --- | ------- | --- | --- | --- | --- | --- | --- | --- |
| [37] Renzo          | Phellan | et al. | Vascular | segmentation | in  | TOF MRA |     |     |     |     |     |     |     |
[56] JohnHCWhitehead.Combinatorialhomotopy.i.Bulletinof
| images | of  | the brain | using | a deep convolutional |     | neural net- |     |     |     |     |     |     |     |
| ------ | --- | --------- | ----- | -------------------- | --- | ----------- | --- | --- | --- | --- | --- | --- | --- |
theAmericanMathematicalSociety,55(3):213–245,1949.4
| work. | InMICCAIWorkshop,pages39–46.Springer,2017. |     |     |     |     |     |           |          |     |                     |     |       |             |
| ----- | ------------------------------------------ | --- | --- | --- | --- | --- | --------- | -------- | --- | ------------------- | --- | ----- | ----------- |
|       |                                            |     |     |     |     |     | [57] Mark | W Wright | et  | al. Skeletonization |     | using | an extended |
1
|     |     |     |     |     |     |     | euclideandistancetransform. |     |     |     | ImageandVisionComputing, |     |     |
| --- | --- | --- | --- | --- | --- | --- | --------------------------- | --- | --- | --- | ------------------------ | --- | --- |
[38] MarkusRempfleretal.Efficientalgorithmsformorallineage
|                           |                             |     |        |                          |     |     | 13(5):367–375,1995. |     |       | 4            |     |            |           |
| ------------------------- | --------------------------- | --- | ------ | ------------------------ | --- | --- | ------------------- | --- | ----- | ------------ | --- | ---------- | --------- |
| tracing.                  | InICCV,pages4695–4704,2017. |     |        |                          | 2   |     |                     |     |       |              |     |            |           |
|                           |                             |     |        |                          |     |     | [58] Aaron          | Wu, | Ziyue | Xu, Mingchen |     | Gao, Mario | Buty, and |
| [39] OlafRonnebergeretal. |                             |     | U-net: | Convolutionalnetworksfor |     |     |                     |     |       |              |     |            |           |
DanielJMollura.Deepvesseltracking:Ageneralizedprob-
MICCAI,
| biomedical         |     | image | segmentation. | In  |     | pages 234– |                                   |     |     |     |     |                   |     |
| ------------------ | --- | ----- | ------------- | --- | --- | ---------- | --------------------------------- | --- | --- | --- | --- | ----------------- | --- |
|                    |     |       |               |     |     |            | abilisticapproachviadeeplearning. |     |     |     |     | In2016IEEE13thIn- |     |
| 241.Springer,2015. |     |       | 6             |     |     |            |                                   |     |     |     |     |                   |     |
ternationalSymposiumonBiomedicalImaging(ISBI),pages
| [40] AzrielRosenfeld.              |     |     | Digitaltopology. | TheAmericanMathe-              |     |     |                      |     |               |     |                        |     |     |
| ---------------------------------- | --- | --- | ---------------- | ------------------------------ | --- | --- | -------------------- | --- | ------------- | --- | ---------------------- | --- | --- |
|                                    |     |     |                  |                                |     |     | 1363–1367.IEEE,2016. |     |               | 2   |                        |     |     |
| maticalMonthly,86(8):621–630,1979. |     |     |                  |                                | 11  |     |                      |     |               |     |                        |     |     |
|                                    |     |     |                  |                                |     |     | [59] YunZengetal.    |     | Topologycuts: |     | Anovelmin-cut/max-flow |     |     |
| [41] MatthiasSchneideretal.        |     |     |                  | Tissuemetabolismdrivenarterial |     |     |                      |     |               |     |                        |     |     |
algorithmfortopologypreservingsegmentationinn–dim-
| treegeneration. |     | MedImageAnal.,16(7):1397–1414,2012. |     |     |     |     |       |                         |     |     |     |     |     |
| --------------- | --- | ----------------------------------- | --- | --- | --- | --- | ----- | ----------------------- | --- | --- | --- | --- | --- |
|                 |     |                                     |     |     |     |     | ages. | CVIU,112(1):81–90,2008. |     |     | 2   |     |     |
6
|                             |     |     |                               |     |     |     | [60] Shan    | Zhao | et al. Cellular | and | molecular | probing | of intact |
| --------------------------- | --- | --- | ----------------------------- | --- | --- | --- | ------------ | ---- | --------------- | --- | --------- | ------- | --------- |
| [42] MatthiasSchneideretal. |     |     | Joint3-Dvesselsegmentationand |     |     |     |              |      |                 |     |           |         |           |
|                             |     |     |                               |     |     |     | humanorgans. |      | Cell,2020.      | 2   |           |         |           |
centerlineextractionusingobliqueHoughforestswithsteer-
| ablefilters.                       |           | MedImageAnal.,19(1):220–249,2015. |        |                       |          | 1          |     |     |     |     |     |     |     |
| ---------------------------------- | --------- | --------------------------------- | ------ | --------------------- | -------- | ---------- | --- | --- | --- | --- | --- | --- | --- |
| [43] Florent                       | Se´gonne. |                                   | Active | contours under        | topology | con-       |     |     |     |     |     |     |     |
| trol—genus                         |           | preserving                        | level  | sets. International   |          | Journal of |     |     |     |     |     |     |     |
| ComputerVision,79(2):107–117,2008. |           |                                   |        |                       | 2        |            |     |     |     |     |     |     |     |
| [44] FrankYShihandChristopherCPu.  |           |                                   |        | Askeletonizationalgo- |          |            |     |     |     |     |     |     |     |
rithmbymaximatrackingoneuclideandistancetransform.
| PatternRecognition,28(3):331–341,1995. |     |     |     |     | 4   |     |     |     |     |     |     |     |     |
| -------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
[45] JoesStaal,MichaelDAbra`moff,MeindertNiemeijer,MaxA
Viergever,andBramVanGinneken.Ridge-basedvesselseg-
| mentationincolorimagesoftheretina.            |     |          |                                     |      | IEEEtransactions |           |     |     |     |     |     |     |     |
| --------------------------------------------- | --- | -------- | ----------------------------------- | ---- | ---------------- | --------- | --- | --- | --- | --- | --- | --- | --- |
| onmedicalimaging,23(4):501–509,2004.          |     |          |                                     |      | 6                |           |     |     |     |     |     |     |     |
| [46] JanStuhmeretal.                          |     |          | Treeshapepriorswithconnectivitycon- |      |                  |           |     |     |     |     |     |     |     |
| straintsusingconvexrelaxationongeneralgraphs. |     |          |                                     |      |                  | InICCV,   |     |     |     |     |     |     |     |
| pages2336–2343,2013.                          |     |          | 2                                   |      |                  |           |     |     |     |     |     |     |     |
| [47] Carole                                   | H   | Sudre et | al. Generalised                     | dice | overlap          | as a deep |     |     |     |     |     |     |     |
learninglossfunctionforhighlyunbalancedsegmentations.
| InMICCAIWorkshop,pages240–248.Springer,2017. |      |          |       |                  |     | 6            |     |     |     |     |     |     |     |
| -------------------------------------------- | ---- | -------- | ----- | ---------------- | --- | ------------ | --- | --- | --- | --- | --- | --- | --- |
| [48] Abdel                                   | Aziz | Taha and | Allan | Hanbury. Metrics |     | for evaluat- |     |     |     |     |     |     |     |
ing3Dmedicalimagesegmentation:analysis,selection,and
| tool.                 | BMCMedicalImaging,15(1):29,2015. |     |                                       |                   | 2   |            |     |     |     |     |     |     |     |
| --------------------- | -------------------------------- | --- | ------------------------------------- | ----------------- | --- | ---------- | --- | --- | --- | --- | --- | --- | --- |
| [49] GilesTettehetal. |                                  |     | Deepvesselnet:Vesselsegmentation,cen- |                   |     |            |     |     |     |     |     |     |     |
| terline               | prediction,                      |     | and bifurcation                       | detection         | in  | 3-d angio- |     |     |     |     |     |     |     |
| graphic               | volumes.                         |     | arXiv preprint                        | arXiv:1803.09340, |     | 2018.      |     |     |     |     |     |     |     |
5,6
| [50] Mihail | Ivilinov | Todorov, | Johannes | C. Paetzold, |     | et al. Au- |     |     |     |     |     |     |     |
| ----------- | -------- | -------- | -------- | ------------ | --- | ---------- | --- | --- | --- | --- | --- | --- | --- |
tomatedanalysisofwholebrainvasculatureusingmachine
| learning. | bioRxiv,page613257,2019. |     |     | 1,2,6 |     |     |     |     |     |     |     |     |     |
| --------- | ------------------------ | --- | --- | ----- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

A.Theory-clDiceinDigitalTopology Proposition2. ForanytopologicaldifferencesbetweenV
P
and V , achieving optimal clDice to guarantee homotopy
L
In addition to our Theorem 1 in the main paper, we are
equivalencerequiresaminimumerrorcorrectionofV .
P
providingintuitiveinterpretationsofclDicefromthedigital
topologyperspective. Bettinumbersdescribeandquantify Proof. From Fig 7, any topological differences between
topologicaldifferencesinalgebraictopology.Thefirstthree V P andV L willresultinghostsormissesintheforeground
Betti numbers (β , β , and β ) comprehensively capture or background skeleton. Therefore, removing ghosts and
0 1 2
the manifolds appearing in 2D and 3D topological space. misses are sufficient conditions to remove topological dif-
Specifically, ferences. Without the loss of generalizability, we consider
thecaseofghostsandmissesseparately:
• β representsthenumberofconnected-components,
0
• β representsthenumberofcircularholes,and
1 For a ghost g ⊂ S ,∃asetofpredictedvoxelsE1 ⊂
• β representsthenumberofcavities(Onlyin3D) P
2 {V \ V }suchthatV \ E1 does not create any misses
P L P
and removes g. Without the loss of generalizability, let’s
assume that there is only one ghost g. Now, to remove g,
under a minimum error correction of V , we have to min-
P
imize |E1|. Let’s say an optimum solution E1 exists.
min
Byconstruction,thisimpliesthatV \E1 removesg.
P min
For a miss m ⊂ V(cid:123),∃asetofpredictedvoxelsE2 ⊂
P
{V \ V }suchthatV ∪ E2 does not create any ghosts
L P P
and removes m. Without the loss of generalizability, let’s
Figure6.Examplesofthetopologyproperties.Left,aholein2D,
assume that there is only one miss m. Now, to remove
inthemiddleaholein3Dandrightacavityinsideaspherein3D.
m, under a minimum error correction of V , we have to
P
minimize |E2|. Let’s say an optimum solution E2
Using the concepts of Betti numbers and digital topol- min
exists. By construction, this implies that V ∪ E2
ogy by Kong et al. [23, 40], we formulate the effect of P min
removesm.
topological changes between a true binary mask (V ) and
L
a predicted binary mask (V ) in Fig. 7. We will use the
P
Thus, in the absence of any ghosts and misses, from
followingdefinitionofghostsandmisses,seeFigure7.
Lemma2.1,clDice=1forbothforegroundandbackground.
1. Ghostsinskeleton: Wedefineghostsinthepredicted Finally,Therefore,Theorem1(fromthemainpaper)guar-
skeleton (S ) when S (cid:54)⊂ V . This means the pre- anteeshomotopyequivalence.
P P L
dicted skeleton is not completely included in the true
mask. Inotherwords,thereexistfalse-positivesinthe Lemma 2.1. In the absence of any ghosts and misses
prediction,whichsurviveafterskeletonization. clDice=1.
2. Missesinskeleton: Wedefinemissesinthepredicted Proof. The absence of any ghosts S P ∈ V L implies
skeleton (S P ) when S L (cid:54)⊂ V P . This means the true Tprec=1;andtheabsenceofanymissesS L ∈V P implies
skeleton is not completely included in the predicted Tsens=1. Hence,clDice=1.
mask. In other words, there are false-negatives in the
A.1. Interpretation of the Adaption to Highly Un-
prediction,whichsurviveafterskeletonization.
balancedDataAccordingtoDigitalTopology:
The false positives and false negatives are denoted by
Considering the adaptions we described in the main
V \V andV \V ,respectively,where\denotesasetdif-
P L L P text,thefollowingprovidesanalysisonhowtheseassump-
ferenceoperation. Thelossfunctionaimstominimizeboth
tions and adaptions are funded in the concept of ghosts
errors.Wecallanerrorcorrectiontohappenwhenthevalue
and misses, described in the previous proofs. Importantly,
of a previously false-negative or false-positive voxel flips
the described adaptions are not detrimental to the perfor-
to a correct value. Commonly used voxel-wise loss func-
mance of clDice for our datasets. We attribute this to the
tions,suchasDice-loss,treateveryfalse-positiveandfalse-
non-applicabilityofthenecessaryconditionsspecifictothe
negativeequally,irrespectiveoftheimprovementinregards
background (i.e. II, IV, VI, VII, and IX in Figure A), as
to topological differences upon their individual error cor-
explainedbelow:
rection.Thus,theycannotguaranteehomotopyequivalence
untilandunlesseverysinglevoxeliscorrectlyclassified. In • II. → In tubular structures, all foreground objects are
stark contrast, we show in the following proposition that eccentric (or anisotropic). Therefore isotropic skele-
clDiceguaranteeshomotopyequivalenceunderaminimum tonization will highly likely produce a ghost in the
errorcorrection. foreground.

Topological Properties Topological Differences Effect in Skeleta
(Betti Numbers)
|     |     |     |     | Foreground Skeleta | Background Skeleta |     |
| --- | --- | --- | --- | ------------------ | ------------------ | --- |
D3 ni noitaler ateleks-ygolopot fo ymonoxaT
|     |     |     | I. New CC  is created |     | Ghosts |     |
| --- | --- | --- | --------------------- | --- | ------ | --- |
𝛽
0
|     | Connected  |     | II. CC are merged |     |     | Misses |
| --- | ---------- | --- | ----------------- | --- | --- | ------ |
Components (CC)
|     |     |     | III. A CC is deleted    |     | Misses |        |
| --- | --- | --- | ----------------------- | --- | ------ | ------ |
|     |     |     | IV. New hole is created |     |        | Ghosts |
𝛽
|     | 1   |     | V. Holes are merged |     | Misses |     |
| --- | --- | --- | ------------------- | --- | ------ | --- |
Holes
|     |     |     | VI. A hole is deleted |     |     | Misses |
| --- | --- | --- | --------------------- | --- | --- | ------ |
Ghosts
VII. New cavity is created
𝛽
|     | 2        |     |                           |     | Misses |        |
| --- | -------- | --- | ------------------------- | --- | ------ | ------ |
|     | Cavities |     | VIII. Cavities are merged |     |        |        |
|     |          |     | IX. A Cavity is deleted   |     |        | Misses |
Figure 7. Upper part, left, taxonomy of the iff conditions to preserve topology in 3D using the concept of Betti numbers [23, 24];
interpretedasthenecessaryviolationofskeletonpropertiesforanypossibletopologicalchangeintheterminologyofghostsandmisses
(upperpartright). Lowerpart,intuitivedepictionsofghostsandmissesintheprediction;fortheskeletonoftheforeground(left)andthe
skeletonofthebackground(right).
IV.→Creatingaholeoutsidethelabeledmaskmeans
•
| adding | a ghost in the | foreground. | Creating a hole | in- |     |     |
| ------ | -------------- | ----------- | --------------- | --- | --- | --- |
sidethelabeledmaskisextremelyunlikelybecauseno
suchholesexistinourtrainingdata.
• VI.→Thedeletionofaholewithoutcreatingamissis
extremelyunlikelybecauseofthesparsityofthedata.
| • VII.and | IX. (only for | 3D) → Creating | or removing | a   |     |     |
| --------- | ------------- | -------------- | ----------- | --- | --- | --- |
cavityisveryunlikelybecausenocavitiesexistinour
trainingdata.
B.AdditionalQualitativeResults

| Image | Label | Soft-Dice | Ours |
| ----- | ----- | --------- | ---- |
Figure8.Qualitativeresults:fortheMassachusettsRoaddatasetandfortheDRIVEretinadataset(lastrow).Fromlefttoright,therealimage,thelabel,
thepredictionusingsoft-diceandthepredictionsusingtheproposedLc(α=0.5),respectively. ThefirstthreerowsareU-Netresultsandthefourthrow
isanFCNresult. Thisindicatesthatsoft-clDicesegmentsroadconnectionswhichthesoft-dicelossmisses. Some,butnotall,missedconnectionsare
indicatedwithsolidredarrows,falsepositivesareindicatedwithred-yellowarrows.

|     | Image |     | Label | Soft-Dice |     | Ours |     |
| --- | ----- | --- | ----- | --------- | --- | ---- | --- |
Figure 9. Qualitative results: 2D slices of the 3D vessel dataset for different sized field of views. From left to right, the real image, the label, the
predictionusingsoft-diceandtheU-NetpredictionsusingLc(α=0.4),respectively.Theseimagesshowthatsoft-clDicehelpstobettersegmentthevessel
connections. Importantlythenetworkstrainedusingsoft-diceover-segmentthevesselradiusandsegmentsincorrectconnections. Bothoftheseerrorsare
notpresentwhenwetrainincludingsoft-clDiceintheloss.Some,butnotall,falsepositiveconnectionsareindicatedwithred-yellowarrows.
C.ComparisontoOtherLiterature: a close or highly varying proximity of the foreground el-
|     |     |     |     | ements (as | is the case | for e.g. capillary | vessels, synaptic |
| --- | --- | --- | --- | ---------- | ----------- | ------------------ | ----------------- |
A recent pre-print proposed a region-separation ap- gaps or irregular road intersections). Any two foreground
|               |                |           |                   | objects which | are placed | at a twice-of-kernel-size | distance |
| ------------- | -------------- | --------- | ----------------- | ------------- | ---------- | ------------------------- | -------- |
| proach, which | aims to tackle | the issue | by analysing dis- |               |            |                           |          |
orclosertoeachotherwillpotentiallybeconnectedbythe
| connectedforegroundelements[33]. |     | Startingwiththepre- |     |     |     |     |     |
| -------------------------------- | --- | ------------------- | --- | --- | --- | --- | --- |
dicted distance map, a network learns to close ambiguous trainednetwork.Thisisfacilitatedbythelossfunctioncon-
sideringthegapasaforegroundduetoperformingdilation
| gaps by referring | to a ground | truth map | which is dilated |     |     |     |     |
| ----------------- | ----------- | --------- | ---------------- | --- | --- | --- | --- |
by a five-pixel kernel, which is used to cover the ambigu- inthetrainingstage. Generalizingtheirapproachtosmaller
kernelshasbeendescribedasinfeasibleintheirpaper[33].
| ity. However, | this does | not generalize | to scenarios with |     |     |     |     |
| ------------- | --------- | -------------- | ----------------- | --- | --- | --- | --- |

| D.DatasetsandTrainingRoutine |     |     |     |     |     |     |     | E.2.RoadDataset |      |     |     |     |     |     |
| ---------------------------- | --- | --- | --- | --- | --- | --- | --- | --------------- | ---- | --- | --- | --- | --- | --- |
|                              |     |     |     |     |     |     |     | E.2.1           | FCN: |     |     |     |     |     |
FortheDRIVEvesselsegmentationdataset,weperform
| three-fold                                   | cross-validation |     | with | 30  | images | and deploy | the |          |     |           |           |     |           |     |
| -------------------------------------------- | ---------------- | --- | ---- | --- | ------ | ---------- | --- | -------- | --- | --------- | --------- | --- | --------- | --- |
|                                              |                  |     |      |     |        |            |     | IN(3ch)  |     | → C(3,10) | → C(5,20) |     | → C(7,30) | →   |
| bestperformingmodelonthetestsetwith10images. |                  |     |      |     |        |            | For |          |     |           |           |     |           |     |
|                                              |                  |     |      |     |        |            |     | C(11,30) |     | → C(7,40) | → C(5,50) |     | → C(3,60) | →   |
theMassachusettsRoadsdataset,wechooseasubsetof120
C(1,1)→Out(1)
| images | (ignoring | imaged | without | a   | network | of roads) | for |     |     |     |     |     |     |     |
| ------ | --------- | ------ | ------- | --- | ------- | --------- | --- | --- | --- | --- | --- | --- | --- | --- |
three-foldcross-validationandtestthemodelsonthe13of-
|     |     |     |     |     |     |     |     | E.2.2 | Unet: |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ----- | ----- | --- | --- | --- | --- | --- |
ficialtestimages.ForCREMI,weperformthree-foldcross-
validationon324imagesandteston51images. Forthe3D SameasDriveDataset,exceptweused2x2up-convolutions
synthetic dataset. we perform experiments using 15 vol- instead of bilinear up-sampling followed by a 2D-
| umesfortraining,2forvalidation,and5fortesting. |     |     |     |     |     |     | Forthe |     |     |     |     |     |     |     |
| ---------------------------------------------- | --- | --- | --- | --- | --- | --- | ------ | --- | --- | --- | --- | --- | --- | --- |
convolutionwithkernelsize1.
| Vessapdataset, |     | weuse | 11volumes |     | fortraining, | 2for | vali- |     |     |     |     |     |     |     |
| -------------- | --- | ----- | --------- | --- | ------------ | ---- | ----- | --- | --- | --- | --- | --- | --- | --- |
dation and 4 for testing. In each of these cases, we report E.3.CremiDataset
theperformanceofthemodelwiththehighestclDicescore
|     |     |     |     |     |     |     |     | E.3.1 | Unet: |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ----- | ----- | --- | --- | --- | --- | --- |
onthevalidationset.
SameasRoadDataset.
E.NetworkArchitectures
E.4.3DDataset
| We use | the | following | notation: |     | In(input | channels), |     |       |        |     |     |     |     |     |
| ------ | --- | --------- | --------- | --- | -------- | ---------- | --- | ----- | ------ | --- | --- | --- | --- | --- |
|        |     |           |           |     |          |            |     | E.4.1 | 3DFCN: |     |     |     |     |     |
Out(outputchannels),
|     |     |     |     |     |     |     |     | IN(1or2ch) |     | → C(3,5) | →   | C(5,10) | → C(5,20) | →   |
| --- | --- | --- | --- | --- | --- | --- | --- | ---------- | --- | -------- | --- | ------- | --------- | --- |
B(outputchannels)presentinput,output,andbottleneck
information(forU-Net); C(filter size,outputchannels) C(3,50)→C(1,1)→Out(1)
| denoteaconvolutionallayerfollowedbyReLU |               |          |             |                |           | andbatch-   |        |           |         |            |       |           |       |     |
| --------------------------------------- | ------------- | -------- | ----------- | -------------- | --------- | ----------- | ------ | --------- | ------- | ---------- | ----- | --------- | ----- | --- |
| normalization;                          |               | U(filter | size,output |                | channels) |             | denote | E.4.2     | 3DUnet: |            |       |           |       |     |
| a trans-posed                           | convolutional |          |             | layer followed |           | by ReLU     | and    |           |         |            |       |           |       |     |
|                                         |               |          |             |                |           |             |        | ConvBlock |         | : C (3,out | size) | ≡ C(3,out | size) | →   |
| batch-normalization;                    |               | ↓        | 2 denotes   | maxpooling;    |           | ⊕ indicates |        |           |         | B          |       |           |       |     |
C(3,outsize)→↓2
| concatenation | of   | information |         | from         | an encoder | block.  | We     |              |     |     |              |           |       |     |
| ------------- | ---- | ----------- | ------- | ------------ | ---------- | ------- | ------ | ------------ | --- | --- | ------------ | --------- | ----- | --- |
| had to choose |      | a different | FCN     | architecture |            | for the | Mas-   |              |     |     |              |           |       |     |
|               |      |             |         |              |            |         |        | UpConvBlock: |     | U   | (3,out size) | ≡ U(3,out | size) | →   |
| sachusetts    | road | dataset     | because | we           | realize    | that a  | larger |              |     | B   |              |           |       |     |
model is needed to learn useful features for this complex ⊕→C(3,outsize)
task.
|     |     |     |     |     |     |     |     | Encoder: |     | IN(1or2ch) | → C | (3,32) | → C (3,64) | →   |
| --- | --- | --- | --- | --- | --- | --- | --- | -------- | --- | ---------- | --- | ------ | ---------- | --- |
|     |     |     |     |     |     |     |     |          |     |            |     | B      | B          |     |
E.1.DriveDataset
|     |     |     |     |     |     |     |     | C B | (3,128)→C | B (5,256)→C |     | B (5,512)→B(512) |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --------- | ----------- | --- | ---------------- | --- | --- |
E.1.1 FCN:
|     |     |     |     |     |     |     |     | Decoder | :   | B(512) | → U (3,512) | →   | U (3,256) | →   |
| --- | --- | --- | --- | --- | --- | --- | --- | ------- | --- | ------ | ----------- | --- | --------- | --- |
|     |     |     |     |     |     |     |     |         |     |        | B           |     | B         |     |
IN(3ch) → C(3,5) → C(5,10) → C(5,20) → U (3,128)→U (3,64)→U (3,32)→Out(1)
|     |     |     |     |     |     |     |     | B   |     | B   | B   |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
C(3,50)→C(1,1)→Out(1)
Table2.Totalnumberofparametersforeachofthearchitectures
usedinourexperiment.
| E.1.2 Unet: |     |            |       |     |         |       |     |     | Dataset | Network | Numberofparameters |        |     |     |
| ----------- | --- | ---------- | ----- | --- | ------- | ----- | --- | --- | ------- | ------- | ------------------ | ------ | --- | --- |
|             |     |            |       |     |         |       |     |     | Drive   | FCN     |                    | 15.52K |     |     |
| ConvBlock   | :   | C B (3,out | size) | ≡   | C(3,out | size) | →   |     |         |         |                    |        |     |     |
|             |     |            |       |     |         |       |     |     |         | UNet    |                    | 28.94M |     |     |
C(3,outsize)→↓2
|              |     |          |     |       |           |       |     |     | Road  | FCN    |     | 279.67K |     |     |
| ------------ | --- | -------- | --- | ----- | --------- | ----- | --- | --- | ----- | ------ | --- | ------- | --- | --- |
|              |     |          |     |       |           |       |     |     | Cremi | UNet   |     | 31.03M  |     |     |
| UpConvBlock: |     | U (3,out |     | size) | ≡ U(3,out | size) | →   |     |       |        |     |         |     |     |
|              |     | B        |     |       |           |       |     |     | 3D    | FCN2ch |     | 58.66K  |     |     |
⊕→C(3,outsize)
|         |           |     |     |            |     |             |     |     |     | Unet2ch |     | 19.21M |     |     |
| ------- | --------- | --- | --- | ---------- | --- | ----------- | --- | --- | --- | ------- | --- | ------ | --- | --- |
| Encoder | : IN(3ch) |     | →   | C B (3,64) | →   | C B (3,128) | →   |     |     |         |     |        |     |     |
F.SoftSkeletonizationAlgorithm
| C (3,256)→C   |           | (3,512)→C   |     | (3,1024)→B(1024) |     |           |     |     |     |     |     |     |     |     |
| ------------- | --------- | ----------- | --- | ---------------- | --- | --------- | --- | --- | --- | --- | --- | --- | --- | --- |
| B             |           | B           |     | B                |     |           |     |     |     |     |     |     |     |     |
| Decoder       | : B(1024) |             | → U | (3,1024)         | →   | U (3,512) | →   |     |     |     |     |     |     |     |
|               |           |             |     | B                |     | B         |     |     |     |     |     |     |     |     |
| U B (3,256)→U |           | B (3,128)→U |     | B (3,64)→Out(1)  |     |           |     |     |     |     |     |     |     |     |

|     |     |     |      |     |     |     |        | delta  | = F.relu(img−img1) |                            |     |     |     |
| --- | --- | --- | ---- | --- | --- | --- | ------ | ------ | ------------------ | -------------------------- | --- | --- | --- |
|     |     |     |      |     |     |     |        | skel = | skel               | + F.relu(delta−skel*delta) |     |     |     |
|     |     | -   | ReLU |     |     |     | return | skel   |                    |                            |     |     |     |
S
1
MinPool
|     | MaxPool |     |     |     | I-S |     | G.3.soft-skeletonizationin3D |     |     |     |     |     |     |
| --- | ------- | --- | --- | --- | --- | --- | ---------------------------- | --- | --- | --- | --- | --- | --- |
1
|     |     | -   | ReLU |     | ×   | +   |                            |     |     |     |      |     |     |
| --- | --- | --- | ---- | --- | --- | --- | -------------------------- | --- | --- | --- | ---- | --- | --- |
|     |     |     |      |     |     | S   | import torch.nn.functional |     |     |     | as F |     |     |
2
| MinPool | MaxPool |     |     |     |     |     |     |     |     |     |     |     |     |
| ------- | ------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
…
|     |     |     |     |     | I-S |     | def soft | erode(img): |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | -------- | ----------- | --- | --- | --- | --- | --- |
n-1
|         |     |     |      |     |     |     | p1 = | −F.max | pool3d(−img,(3,1,1),(1,1,1),(1,0,0)) |     |     |     |     |
| ------- | --- | --- | ---- | --- | --- | --- | ---- | ------ | ------------------------------------ | --- | --- | --- | --- |
|         |     | … - | ReLU |     | ×   | +   |      |        |                                      |     |     |     |     |
|         |     |     |      |     |     |     | p2 = | −F.max | pool3d(−img,(1,3,1),(1,1,1),(0,1,0)) |     |     |     |     |
| …       |     |     |      |     |     |     | p3 = | −F.max | pool3d(−img,(1,1,3),(1,1,1),(0,0,1)) |     |     |     |     |
| MinPool |     |     |      |     |     | S n |      |        |                                      |     |     |     |     |
MaxPool
|     |     |     |     |     |     |     | return   | torch.min(torch.min(p1, |                                     |     |     | p2), p3) |     |
| --- | --- | --- | --- | --- | --- | --- | -------- | ----------------------- | ----------------------------------- | --- | --- | -------- | --- |
|     |     |     |     |     |     |     | def soft | dilate(img):            |                                     |     |     |          |     |
|     |     |     |     |     | S   |     | return   | F.max                   | pool3d(img,(3,3,3),(1,1,1),(1,1,1)) |     |     |          |     |
final
|     |     |     |     |     |     |     | def soft | open(img): |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | -------- | ---------- | --- | --- | --- | --- | --- |
Figure10.Schemeofourproposeddifferentiableskeletonization.
|                                |     |                                         |     |                           |                    |     | return   | soft      | dilate(soft    |         | erode(img)) |     |     |
| ------------------------------ | --- | --------------------------------------- | --- | ------------------------- | ------------------ | --- | -------- | --------- | -------------- | ------- | ----------- | --- | --- |
| Onthetopleftthemaskinputisfed. |     |                                         |     | Next,                     | theinputisreatedly |     |          |           |                |         |             |     |     |
| erodedanddilated.              |     | Theresultingerosionsanddilationsarecom- |     |                           |                    |     |          |           |                |         |             |     |     |
|                                |     |                                         |     |                           |                    |     | def soft | skel(img, |                | iter ): |             |     |     |
| paredtotheimagebeforedilation. |     |                                         |     | Thedifferencebetweenthise |                    |     |          |           |                |         |             |     |     |
|                                |     |                                         |     |                           |                    |     | img1     | =         | soft open(img) |         |             |     |     |
imagesispartoftheskeletonandwillbeaddediterativelytoob-
|                           |     |     |                                  |     |     |     | skel | = F.relu(img−img1) |            |            |     |     |     |
| ------------------------- | --- | --- | -------------------------------- | --- | --- | --- | ---- | ------------------ | ---------- | ---------- | --- | --- | --- |
|                           |     |     |                                  |     |     |     | for  | j in               | range(iter | ):         |     |     |     |
| tainafullskeletonization. |     |     | TheReLuoperationeliminatespixels |     |     |     |      |                    |            |            |     |     |     |
|                           |     |     |                                  |     |     |     |      | img =              | soft       | erode(img) |     |     |     |
thatweregeneratedbythedilationbutarenotpartoftheoirginal
|     |     |     |     |     |     |     |     | img1 | = soft | open(img) |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ---- | ------ | --------- | --- | --- | --- |
orerodedimage.
|         |     |            |     |            |         |     |        | delta | = F.relu(img−img1) |                            |     |     |     |
| ------- | --- | ---------- | --- | ---------- | ------- | --- | ------ | ----- | ------------------ | -------------------------- | --- | --- | --- |
|         |     |            |     |            |         |     |        | skel  | = skel             | + F.relu(delta−skel*delta) |     |     |     |
|         |     |            |     |            |         |     | return | skel  |                    |                            |     |     |     |
| G. Code | for | the clDice |     | similarity | measure | and |        |       |                    |                            |     |     |     |
thesoft-clDiceloss(PyTorch):
H.EvaluationMetrics
G.1.clDicemeasure
Asdiscusedinthetext,wecomparetheperformanceofvar-
from skimage.morphology import skeletonize iousexperimentalsetupsusingthreetypesofmetrics: vol-
| import | numpy    | as np                 |     |     |     |     | umetric,graph-basedandtopology-based. |     |     |     |     |     |     |
| ------ | -------- | --------------------- | --- | --- | --- | --- | ------------------------------------- | --- | --- | --- | --- | --- | --- |
| def cl | score(v, | s):                   |     |     |     |     |                                       |     |     |     |     |     |     |
| return |          | np.sum(v*s)/np.sum(s) |     |     |     |     |                                       |     |     |     |     |     |     |
H.1. Overlap-based:
| def clDice(v |     | p, v       | l):             |                |     |     |      |              |          |     |             |     |           |
| ------------ | --- | ---------- | --------------- | -------------- | --- | --- | ---- | ------------ | -------- | --- | ----------- | --- | --------- |
| tprec        | =   | cl score(v | p,skeletonize(v |                |     | l)) |      |              |          |     |             |     |           |
|              |     |            |                 |                |     |     | Dice | coefficient, | Accuracy |     | and clDice, | we  | calculate |
| tsens        | =   | cl score(v | l               | ,skeletonize(v |     | p)) |      |              |          |     |             |     |           |
return 2*tprec*tsens/(tprec+tsens) thesescoresonthewhole2D/3Dvolumes. clDiceiscalcu-
|                              |     |     |     |     |     |     | lated using         | a morphological |     | skeleton | (skeletonize3D |     | from |
| ---------------------------- | --- | --- | --- | --- | --- | --- | ------------------- | --------------- | --- | -------- | -------------- | --- | ---- |
| G.2.soft-skeletonizationin2D |     |     |     |     |     |     | theskimagelibrary). |                 |     |          |                |     |      |
H.2.Graph-based:
| import   | torch.nn.functional |     |     | as F |     |     |     |     |     |     |     |     |     |
| -------- | ------------------- | --- | --- | ---- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| def soft | erode(img):         |     |     |      |     |     |     |     |     |     |     |     |     |
Weextractgraphsfromrandompatchesof64×64pixels
| p1  | = −F.max | pool2d(−img, |     | (3,1), | (1,1), | (1,0)) |     |     |     |     |     |     |     |
| --- | -------- | ------------ | --- | ------ | ------ | ------ | --- | --- | --- | --- | --- | --- | --- |
p2 = −F.max pool2d(−img, (1,3), (1,1), (0,1)) in2Dand48×48×48in3Dimages.
| return |     | torch.min(p1,p2) |     |     |     |     |         |                     |     |     |       |                  |     |
| ------ | --- | ---------------- | --- | --- | --- | --- | ------- | ------------------- | --- | --- | ----- | ---------------- | --- |
|        |     |                  |     |     |     |     | For the | StreetmoverDistance |     |     | (SMD) | [4] we uniformly |     |
sampleafixednumberofpointsfromthegraphofthepre-
| def soft | dilate(img): |     |     |     |     |     |     |     |     |     |     |     |     |
| -------- | ------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
return F.max pool2d(img, (3,3), (1,1), (1,1)) dictionandlabel,matchthemandcalculatetheWasserstein-
|     |     |     |     |     |     |     | distancebetweenthesegraphs. |     |     | Forthejunction-basedmet- |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --------------------------- | --- | --- | ------------------------ | --- | --- | --- |
def soft open(img): ric(Opt-J)wecomputetheF1scoreofjunction-basedmet-
| return |     | soft dilate(soft |     | erode(img)) |     |     |                |          |     |         |           |          |       |
| ------ | --- | ---------------- | --- | ----------- | --- | --- | -------------- | -------- | --- | ------- | --------- | -------- | ----- |
|        |     |                  |     |             |     |     | rics, recently | proposed |     | by [7]. | According | to their | paper |
def soft skel(img, iter): thismetricisadvantageousoverallpreviousjunction-based
img1 = soft open(img) metricsasitcanaccountfornodeswithanarbitrarynumber
| skel | =   | F.relu(img−img1) |     |     |     |     |     |     |     |     |     |     |     |
| ---- | --- | ---------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
ofincidentedges,makingthismetricmoresensitivetoend-
| for | j in | range(iter): |            |     |     |     |            |        |             |     |           |           |     |
| --- | ---- | ------------ | ---------- | --- | --- | --- | ---------- | ------ | ----------- | --- | --------- | --------- | --- |
|     |      |              |            |     |     |     | points and | missed | connections | in  | predicted | networks. | For |
|     | img  | = soft       | erode(img) |     |     |     |            |        |             |     |           |           |     |
img1 = soft open(img) moreinformationpleaserefortotheirpaper.

H.3.Topology-based:
Fortopology-basedscoreswecalculatetheBettiErrors
| for | the Betti Numbers | β   | and β . | Also, | we calculate | the |
| --- | ----------------- | --- | ------- | ----- | ------------ | --- |
|     |                   | 0   | 1       |       |              |     |
Eulercharacteristic,χ=V−E+F,whereEisthenumber
| ofedges,F | isthenumberoffacesandV |              |       |                | isthenumberof |       |
| --------- | ---------------------- | ------------ | ----- | -------------- | ------------- | ----- |
| vertices. | We report              | the relative | Euler | characteristic |               | error |
| (χ        | ), as the              | ratio of the | χ of  | the predicted  | mask          | and   |
ratio
| thatofthegroundtruth. |     | Notethataχ |     |     | closertooneis |     |
| --------------------- | --- | ---------- | --- | --- | ------------- | --- |
ratio
preferred.Allthreetopology-basedscoresarecalculatedon
randompatchesof64×64pixelsin2Dand48×48×48
in3Dimages.
I.AdditionalQuantitativeResults
| Table          | 3. Quantitative                        | experimental | results | for | the 3D | synthetic |
| -------------- | -------------------------------------- | ------------ | ------- | --- | ------ | --------- |
| vesseldataset. | Boldnumbersindicatethebestperformance. |              |         |     |        | We        |
trainedbaselinemodelsofbinary-cross-entropy(BCE),softDice
andmean-squared-errorloss(MSE)andcombinedthemwithour
| soft-clDiceandvariedtheα>0. |     |                                 | Forallexperimentsweobserve |     |     |     |
| --------------------------- | --- | ------------------------------- | -------------------------- | --- | --- | --- |
| thatusingsoft-clDiceinL     |     | resultsinimprovedscorescompared |                            |     |     |     |
c
| to soft-Dice. | This | improvement | holds | for almost | α   | > 0. We |
| ------------- | ---- | ----------- | ----- | ---------- | --- | ------- |
observethatsoft-clDicecanbeefficientlycombinedwithallthree
frequentlyusedlossfunctions.
|     | Loss     |     | Dice  | clDice |     |     |
| --- | -------- | --- | ----- | ------ | --- | --- |
|     | BCE      |     | 99.81 | 98.24  |     |     |
|     | L ,α=0.5 |     | 99.76 | 98.25  |     |     |
c
|     | L ,α=0.4 |     | 99.77 | 98.29 |     |     |
| --- | -------- | --- | ----- | ----- | --- | --- |
c
|     | L c ,α=0.3 |     | 99.76 | 98.20 |     |     |
| --- | ---------- | --- | ----- | ----- | --- | --- |
|     | L ,α=0.2   |     | 99.78 | 98.29 |     |     |
c
|     | L ,α=0.1  |     |       |       |     |     |
| --- | --------- | --- | ----- | ----- | --- | --- |
|     | c         |     | 99.82 | 98.39 |     |     |
|     | L ,α=0.01 |     | 99.83 | 98.46 |     |     |
c
|     | L ,α=0.001 |     | 99.85 | 98.42 |     |     |
| --- | ---------- | --- | ----- | ----- | --- | --- |
c
|     | soft-Dice |     | 99.74 | 97.07 |     |     |
| --- | --------- | --- | ----- | ----- | --- | --- |
|     | L ,α=0.5  |     | 99.74 | 97.53 |     |     |
c
|     | L c ,α=0.4 |     | 99.74 | 97.07 |     |     |
| --- | ---------- | --- | ----- | ----- | --- | --- |
|     | L ,α=0.3   |     | 99.80 | 98.13 |     |     |
c
|     | L ,α=0.2 |     | 99.74 | 97.08 |     |     |
| --- | -------- | --- | ----- | ----- | --- | --- |
c
|     | L ,α=0.1 |     | 99.74 | 97.08 |     |     |
| --- | -------- | --- | ----- | ----- | --- | --- |
c
|     | L ,α=0.01 |     | 99.74 | 97.07 |     |     |
| --- | --------- | --- | ----- | ----- | --- | --- |
c
|     | L c ,α=0.001 |     | 99.74 | 97.12 |     |     |
| --- | ------------ | --- | ----- | ----- | --- | --- |
|     | MSE          |     | 99.71 | 97.03 |     |     |
|     | L c ,α=0.5   |     | 99.62 | 98.22 |     |     |
|     | L ,α=0.4     |     | 99.65 | 97.04 |     |     |
c
|     | L ,α=0.3 |     | 99.67 | 98.16 |     |     |
| --- | -------- | --- | ----- | ----- | --- | --- |
c
|     | L c ,α=0.2 |     | 99.70 | 97.10 |     |     |
| --- | ---------- | --- | ----- | ----- | --- | --- |
|     | L ,α=0.1   |     | 99.74 | 98.21 |     |     |
c
|     | L ,α=0.01 |     | 99.82 | 98.32 |     |     |
| --- | --------- | --- | ----- | ----- | --- | --- |
c
|     | L ,α=0.001 |     | 99.84 | 98.37 |     |     |
| --- | ---------- | --- | ----- | ----- | --- | --- |
c