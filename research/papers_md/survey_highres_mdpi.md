sensors
Review
A Survey of Deep Learning Road Extraction Algorithms Using
High-Resolution Remote Sensing Images
ShaoyiMo1 ,YufengShi1,* ,QiYuan1andMingyueLi2
1 CollegeofCivilEngineering,NanjingForestryUniversity,Nanjing210047,China;
moshaoyi@njfu.edu.cn(S.M.);yq@njfu.edu.cn(Q.Y.)
2 SchoolofForeignStudies,NanjingForestryUniversity,Nanjing210047,China;mylee@njfu.edu.cn
* Correspondence:yfshi@njfu.edu.cn
Abstract:Roadsarethefundamentalelementsoftransportation,connectingcitiesandruralareas,
as well as people’s lives and work. They play a significant role in various areas such as map
updates,economicdevelopment,tourism,anddisastermanagement.Theautomaticextractionof
roadfeaturesfromhigh-resolutionremotesensingimageshasalwaysbeenahotandchallengingtopic
inthefieldofremotesensing,anddeeplearningnetworkmodelsarewidelyusedtoextractroads
fromremotesensingimagesinrecentyears.Inlightofthis,thispapersystematicallyreviewsand
summarizesthedeep-learning-basedtechniquesforautomaticroadextractionfromhigh-resolution
remotesensingimages.Itreviewstheapplicationofdeeplearningnetworkmodelsinroadextraction
tasksandclassifiesthesemodelsintofullysupervisedlearning,semi-supervisedlearning,andweakly
supervisedlearningbasedontheiruseoflabels. Finally, asummaryandoutlookofthecurrent
developmentofdeeplearningtechniquesinroadextractionareprovided.
Keywords: road extraction; high-resolution remote sensing images; deep learning; supervised
learning;networkmodel
1. Introduction
Citation:Mo,S.;Shi,Y.;Yuan,Q.;Li, There are various types of roads in remote sensing images, such as urban roads,
M.ASurveyofDeepLearningRoad suburbanroads,mountainroads,expressways,overpasses,etc. Astheresolutionofremote
ExtractionAlgorithmsUsing sensingimagescontinuestoimprove,high-resolutionimagescontainmoreinformation
High-ResolutionRemoteSensing aboutthetexture, shape, structure, andneighborhoodrelationshipsofroadscompared
Images.Sensors2024,24,1708. to low- and medium-resolution remote sensing images, enabling more accurate road
https://doi.org/10.3390/ informationextraction[1]. Extractingroadinformationfromhigh-qualityremotesensing
s24051708
imageshasalwaysbeenchallengingduetomultiplefactors. Theseincludecomplexand
AcademicEditor:YunZhang cluttered backgrounds (such as buildings, vegetation, and various road types), diverse
road shapes (which vary in width and length), and poor image perspectives (resulting
Received:15January2024
fromocclusionsbycloudsandfog,aswellaslightingeffects). Furthermore,asurbanareas
Revised:26February2024
expand,thetopologicalstructureofroadsbecomesexceptionallycomplex,withnumerous
Accepted:4March2024
buildingsobstructinglargeportionsofroadareas[2].
Published:6March2024
Roadextractionistypicallyregardedasasemanticsegmentationtask,whereroadand
non-roadlabelsareassignedtoallpixelsinanimage,achievingbinarysemanticsegmenta-
tion. Withtherapidadvancementofdeeplearning,therehasbeenwidespreadinterestin
Copyright: © 2024 by the authors. itspowerfuldatafittingandinformationprocessingcapabilities. Previousreviewshave
Licensee MDPI, Basel, Switzerland. focusedontheprogressofroadextractiontechniquesinremotesensingimages. Theysum-
Thisarticleisanopenaccessarticle marizebothtraditionalanddeeplearningmethods. Forinstance,Abdollahietal.[3]sum-
distributed under the terms and marizedroadextractionmethodsinremotesensingimageryasbeingbasedondeeplearn-
conditionsoftheCreativeCommons ingtechniques,suchasDCNN[4],FCN[5],deconvolution[6],andGANs[7]. Lianetal.[8]
Attribution(CCBY)license(https:// furthercategorizedextractionmethodsintoheuristicanddata-drivenroadextractionap-
creativecommons.org/licenses/by/ proaches. Heuristicmethodspredominantlyemploysemi-automaticorfullyautomatic
4.0/).
Sensors2024,24,1708.https://doi.org/10.3390/s24051708 https://www.mdpi.com/journal/sensors

Sensors2024,24,1708 2of31
traditionaltechniquesforroadextraction,suchassnakemodel-basedcontourextraction[9],
geodesic path-based approaches [10], dynamic programming-based methods [11], and
template matching [12]. Automated extraction methods include machine learning seg-
mentation algorithms like SVM [13], K-Means [14], and Bayesian classifiers [15], edge
analysis-basedmethods[16], andmap-basedtechniques[17]. Thedata-drivenmodule,
basedon[3],alsoaddsasummaryofgraph-basedmethods[18]. Jiaetal.[19]discussed
theapplicationsofactiveandpassiveremotesensingtechnologiesinroadextraction,in-
cludinghigh-resolution,hyperspectral,syntheticapertureradar(SAR),andairbornelaser
scanning(ALS)technologies,andalsoprovidedasummaryofthecurrentstateandfuture
prospectsofmulti-sourcedatafusion. Liuetal.[20]summarizedpreviousdata-driven
methods as fully supervised learning methods and introduced weakly supervised and
unsupervisedlearningmethods. Currently,mainstreamroadextractionnetworkmodels
canbebroadlycategorizedintofullysupervisedandsemi-supervised(weaklysupervised)
extraction. Thedifferentiationbetweenthesetwolearningmethodsprimarilydependson
whetherthemodelrequiressubstantiallabeldatasupportduringtraining.Fullysupervised
learningrelies onalargenumber ofpixel-leveltraininglabelsformodeltraining. This
approach often achieves high-precision segmentation structures, but its generalization
capabilityisrelativelyweak,resultinginlimitedsegmentationperformanceinunknown
scenarios. Moreover, obtaining pixel-level labels often requires a significant amount of
manualannotationwork,andtheseannotateddataexhibitahighdegreeofsubjectivity,
potentiallyimpactingtheaccuracyofroadsegmentationbythemodel. Semi-supervised
(weak)learningreliesonfewertraininglabeldata,whichcanbeintheformofpoints,lines,
andotherweaklabelsformodeltraining. Whilesemi-supervised(weak)learninggenerally
lagsbehindinsegmentationperformancecomparedtofullysupervisedlearning,itoffers
certainadvantages. Thisapproachreducesthedependencyonlabeldata,thusalleviating
theburdenofmanualannotation.
To address issues of insufficient labels and high annotation costs in road extrac-
tiontaskshttps://www.isprs.org/education/benchmarks/UrbanSemLab/(accessedon2
March2024),thispaperclassifiesnetworkmodelsbasedontheuseofpixel-levellabels,
including fully supervised learning, semi-supervised learning, and weakly supervised
learning. Inthispaper, “roadextraction”, “deeplearning”, and“remotesensing”were
chosenassearchingkeywords. TheWebofScience(WOS)andGoogleScholardatabases
were used as literature search tools to primarily retrieve relevant literature from 2020
to2023. Weorganizedthepubliclyavailabledatasetsmentionedintheretrievedlitera-
tureover40datasets(2013–2023). Thiscompilationincludes22publiclyaccessibleroad
datasets,withimagesprimarilysourcedfromGoogleEarth,OpenStreetMap(OSM),open
APIs,droneimagery,andsatelliteimagery,coveringurban,suburban,rural,andforested
areas. Furthermore,weobservedthatmultiplepubliclyavailableroaddatasetssuchas
Massachusetts[21],ISPRS1,CasNet[22],DeepGlobe[23],SpaceNet[24],Roadtracer[25],
Ottawa [26], and CHN6-CUG [27] were utilized two or more times between 2020 and
2023,asdepictedinFigure1. InFigure1,theleftmostcolumnrepresentsthenumberof
timesdatasetswereusedduringthesefouryears,whiletherightmostcolumnindicates
thenumberoftimescorrespondingnetworkmodelsutilizedthedatasets. Additionally,
we conducted research on pre-processing and post-processing work related to remote
sensingimagesintherelevantliterature. Forinstance,areal-timemulti-temporalcolor
dataenhancementtechniquewasintroducedforimprovingSentinel-1multi-polarization
andSentinel-2multi-spectralimagerydatasets[28]. Imagequalitywasenhancedthrough
theapplicationofthecontrast-limitedadaptivehistogramequalization(CLAHE)algorithm
tomitigatemountainshadowissues[29]. Post-processingtasksincludedroadvectoriza-
tion [30], road information, and label reconstruction [31], among others. Due to space
constraints, thispaperprimarilyfocusesontheanalysisanddiscussionofroadfeature
extractionresearchbasedonfullysuperviseddeeplearningnetworkmodels. Thestructure
ofthispaperisasfollows: Section1introducesandbrieflyelucidatesthechallengesand
methods in the field of road extraction from remote sensing images. Section 2 delves

Sensors 2024, 24, x FOR PEER REVIEW 3 of 32
Sensors2024,24,1708 3of31
methods in the field of road extraction from remote sensing images. Section 2 delves into
irnotaodr ofeaadtufreea teuxrteraecxtitornac utisoinngu fsuinllgy fsuulplyersvuispeedr vdieseepd ldeeaernpinlega rnneitnwgonrke tmwoodrkelsm wodhielles swtuhdilye-
sintugd tyhien gstrtehnegstthrse nagntdh slimanidtatliiomnist aotfi otnhessoef nthetewseornke tmwoodreklsm. Soedcetliso.nS 3e cetxiopnlo3reesx rpolaodre fsearotuarde
feexattruarcetieoxnt rtahcrtoiounghth sreomugi-hsuspeemrvi-issuepde (rwviesaekd) (dweeeapk l)edareneipngle.a Srencitniogn. S4e pctrieosnen4tps rae sceonmtsparechoemn--
psirveeh erenvsiievwe roefv rioeawd oefxtrroaacdtioenx tmraectthioondomloegthieosd, coolongdiuecst,icnogn ad cuocmtinpgaraatcivoem apnaarlaytsiivse oaf ndaivlyesrsise
omfoddivelesr isne tmeromdse losf itnheteirr mpesrfoofrmthaenircep.e Urflotirmmaatnelcye,. wUel toibmjeactteivlye,lyw deioscbujescs ttihvee llyimdiitsactuiosnsst hine-
lhimerietnatti oinn scuinrrheenrte nsutpinercvuirsreedn tlesaurpneinrvgi smedodleealsr.n Sinecgtimono d5e plsu.tS feocrtwioanrd5sp fuuttuforrew parrodsspfeucttsu roef
proroasdp eexcttrsaocftiroona adnedx tcrhaacltlieonngaesn.d challenges.
Figure 1. Public datasets used more than twice from 2020–2023.
Figure1.Publicdatasetsusedmorethantwicefrom2020–2023.
22.. RRooaadd FFeeaattuurree EExxttrraaccttiioonn BBaasseedd oonn FFuullllyyS SuuppeerrvviisseeddD DeeeeppL LeeaarrnnininggN NeetwtwoorkrkM odels
ModMelns ih[32]firstintroducedconvolutionalneuralnetworks(CNNs)intoroadextraction
tasksM. Inniihti a[3ll2y], fiinrstth ienfitreoldduocfedd eceopnvleoalruntiionngaflo nreruoraadl nexettwraocrtikosn (,CmNaNnys) riensteoa rrochader sexutsraecd-
btiloonck t-absaksse. dInCitNiaNllym, iond tehles tfioepldr oocfe dsseerpoa ldeasrwniinthgi nfoirm raogaeds e.xFtorracetxiaomn,p mlea,nfiyn irteessetaartcehmerasc uhsinede
(bFlSoMck)-banasdepda CtcNh-Nb amseoddCelNs Nto (parsoscheosws rnoiandFs igwuitrhei2n) immeatgheosd. sFwore reexaemmpplloe,y fiedni[t3e3 s]ttaotet rmacak-
acnhdineex (tFrSaMct)r oaandds psaetpcahr-abtaesleyd. TChNeNse (paast cshho-bwanse idn CFiNguNrem 2o)d melesthpoedrfso wrmereed eemxcpellolyenedtl y[3i3n]
atoer tiaralcimk aagneds ewxittrhacat srpoaatdiasl sreepsoalruattieolny.o Tfh1e.2sem pbautcths-tbruasgegdle CdNtoNa cmhioedveelss aptiesrffaocrtmoreydr eesxucletls-
ilnenhtilgyh ienr -areersioallu itmioang(e0s.1 w5imth) aim sapgaetieaxl trreascotliuonti.oTno oafd 1d.2re mss bthuits sitsrsuugeg,Rleedz atoe eaacnhdievZeh asantgis[f3a4c]-
itmorpyr orevseudlttsr aind ihtiiognhaelr-preastcohlu-btiaosne d(0C.1N5 Nm)m imetahgoed se,xetrnaacbtiloinng. Tthoe amddtoreosus ttpheisr fiosrsmues, uRpepzaoeret
vaencdto Zrhmaancgh i[n3e4]( SiVmMpr)omveedth otrdasdiintioronaadl pexattrcahc-tbioansefdro CmNhNig hm-reetshooldusti,o enniambalignegd tahteamse ttso( 0o.u1t5-
mspatialresolution). However,patch-basedCNNmethodsoverlyreliedonthesliding
perform support vector machine (SVM) methods in road extraction from high-resolution
windowapproach,whichinvolvedfeatureextractionthroughconvolutionalandpooling

Sensors 2024, 24, x FOR PEER REVIEW 4 of 32
Sensors 2024, 24, x FOR PEER REVIEW 4 of 32
image datasets (0.15 m spatial resolution). However, patch-based CNN methods overly
image datasets (0.15 m spatial resolution). However, patch-based CNN methods overly
Sensors2024,24,1708 relied on the sliding window approach, which involved feature extraction through con-4of31
relied on the sliding window approach, which involved feature extraction through con-
volutional and pooling layers, followed by backpropagation to fine-tune the final param-
volutional and pooling layers, followed by backpropagation to fine-tune the final param-
eters. This resulted in relatively low extraction efficiency, which was insufficient for meet-
eters. This resulted in relatively low extraction efficiency, which was insufficient for meet-
ing thlaey reerqsu,ifroelmloewnetsd obf yprbaacctikcparl oappapgliactaiotinontos. fiAnded-ittuionneatlhlye, fichnoaolspinarga amne atperpsr.oTphriiastere ssluidlt-edin
ing the requirements of practical applications. Additionally, choosing an appropriate slid-
ing wrienladtoivwe lsyizloe wwaexs tar acchtiaollnenefgfiincige ntacsyk,w. Iht iwchasw naosti unsnutiflfi tchieen etmfoerrgmeenectein ogf tfhuellyre cqounirveomlue-ntsof
ing window size was a challenging task. It was not until the emergence of fully convolu-
practicalapplications. Additionally,choosinganappropriateslidingwindowsizewasa
tional neural networks (FCNs), that this problem was effectively solved. The FCN model
tional neural networks (FCNs), that this problem was effectively solved. The FCN model
challengingtask. Itwasnotuntiltheemergenceoffullyconvolutionalneuralnetworks
was first introduced into the field of image segmentation [35], as shown in Figure 3, and
was first introduced into the field of image segmentation [35], as shown in Figure 3, and
(FCNs),thatthisproblemwaseffectivelysolved. TheFCNmodelwasfirstintroducedinto
it significantly improved segmentation efficiency. In contrast to traditional patch-based
tihte sifigenldifiocfanimtlayg iemspegromveendt asteigomn[e3n5t]a,taiosnsh eoffiwcnieinncFyi.g Iunr ceo3n,tarnasdt ittos tirgandiifiticoannatll ypaimtcphr-boavseedd
CNN models, an FCN is capable of pixel-level image classification, meaning it classifies
sCegNmNe nmtaotdioenls,e affinc FieCnNcy .isI ncacpoanbtlrea sotf tpoixtreal-dleitvioeln iamlpagaetc chl-absassifiedcaCtioNnN, mmeoadneinlsg, aitn cFlaCssNifiiess
each pixel into a category, with the output providing the category for each pixel. The FCN
ceaapcahb pleixoefl pinixtoel a-l ecavteelgiomrayg, wecitlhas tshifie coauttiopnu,t mpreoavniidnigngit tchlea scsaitfieegsoerayc fhorp eixaeclhi pnitxoeal. cTahteeg FoCryN,
replaces fully connected layers with convolutional layers, achieving end-to-end semantic
wreitphlatcheeso fuutlplyu ctopnrnoevcitdeidn glatyheersc awteitgho rcyonfovroleuatcihonpailx lealy.eTrhse, aFcChNievrienpgl aecneds-ftuol-leyncdo snenmecatnetdic
segmentation. This overcomes the inefficiency issue of patch-based CNN methods and
laseygemrsewntitahtioconn. vTohliust ioovnearlcloamyeerss ,thaceh iineevffiincgieenncdy- tios-seuned osfe mpaatnchti-cbsaesgemd eCnNtaNtio mn.eTthhoisdso vaenrd-
allows for the extraction of target semantic information while preserving spatial infor-
caolmloewsst hfoeri ntheeffi ecxietrnaccytiiosnsu oef otfarpgaettc hse-bmaasendticC iNnfNormmeatthioond swahnidle apllroewsesrvfoinrgt hsepeaxtitarla cintifoonr-
mation [1]. While the FCN enhanced the CNN by enabling pixel-to-pixel classification, it
omftaatriogne t[1se].m Wanhtiliec tinhfeo FrmCNat ieonnhwanhcieled pthrees CerNvNin gbys peantaiablliinngfo primxealt-itoon-p[i1x]e.lW clahsilseifitchaetiFoCnN, it
disregarded the relationships between pixels. Therefore, subsequent models introduced
ednihsarengcaedrdtehde tChNe Nreblaytieonnasbhliipnsg bpeixtwele-teon- ppixixeellcsl.a Tsshiefirceaftoioren,, situdbisserqeguaerndte mdothdeelrse lianttiroondshuicpesd
various attention mechanism modules to strengthen the relationships between pixels. Fur-
bveatrwioeuesn apttiexneltsio.nT hmeercehfoarnei,smsu bmsoedquuelenst tmo sotdreenlsgitnhterno dthuec reedlavtaiorniosuhsipast tbeentwtioenenm peicxhelasn. iFsumr-
thermore, the FCN’s structure has offered novel insights into encoder–decoder network
mthoedrumleosreto, tshtere FnCgtNh’esn stthruecrteulareti ohnassh oipffserbeedtw neoevnelp iinxeslisg.hFtsu rinthtoer emnocroed,ethr–edFeCcoNd’sers tnreutcwtuorrek
architectures.
haarschoiftfeecrteudrenso. velinsightsintoencoder–decodernetworkarchitectures.
Figure 2. Patch-based CNN model.
FFigiguurree2 2..P Paattcchh--bbaasseeddC CNNNNm mooddeel.l.
FigureF i3g.u Fruel3ly. FCuolnlyvoClountivoonlault NioenuarlaNl eNuertawlNorekt w(FoCrNk)( FmCoNd)eml. odel.
Figure 3. Fully Convolutional Neural Network (FCN) model.
2.1. RoadFeatureExtractionBasedonEncoder–DecoderStructure
2.1. Road Feature Extraction Based on Encoder–Decoder Structure
2.1. Road Feature Extraction Based on Encoder–Decoder Structure
FollowingtheFCN,networkstructuresbasedonencodersanddecodershaveemerged
Following the FCN, network structures based on encoders and decoders have
andbFeeonllowwidinegly tahpep lFieCdN. T, hneeirtwooprekra tsitornucintuvroelsv ebsamseudl tiopnle ednocwondsearms palnindg doefctohdeeorrsi ghinaavle
emerged and been widely applied. Their operation involves multiple downsampling of
imemageregbeyd tahnede nbceoedne wrtiodeolbyt aaipnpmlieudlt.i -Tlehveeilr iompaegreatfieoant uinrevoinlvfoersm matuioltnip,lfeo ldloowwendsabmypulpinsagm o-f
the original image by the encoder to obtain multi-level image feature information, fol-
ptlhine gotrhigrionuagl himthaegde ebcyo dthere teonrceosdtoerre tsop oatbitaaliinn fmorumltai-tlieovnel( Fiimguagree 4f)e.aMtuored eilnsfobramseadtioonn,t hfoisl-
lowed by upsampling through the decoder to restore spatial information (Figure 4). Mod-
sltorwucetdu rbeyi nucplsuadmepSleinggN tehtr[o3u6g],hU th-Ne detec[3o7d]e,rP tSoP rNesetto[r3e8 s]p,aLtiinakl Ninefotr[m39a]t,iDone e(FpiLgaubreV 43)+. M[4o0d],-
els based on this structure include SegNet [36], U-Net [37], PSPNet [38], LinkNet [39],
aenlsd bmaoserde. oAnm thoinsg stthruecmtu,rUe -iNnecltuidseo nSeegoNfetht e[3m6]o, sUtc-Nlaests i[c3n7]e,t wPSoPrkNsewt [i3th8]a, LsyinmkmNeett r[i3ca9l],
DeepLab V3+ [40], and more. Among them, U-Net is one of the most classic networks with
UD-esehpaLpaebd Ven3+c o[4d0e]r,– adnedc omdoerre.s Atrumcotunrge t,hienmiti,a Ull-yNaept pisl ioende ionf tmhee dmicoaslt icmlaasgsiec sneegtwmoernktsa twioitnh
a symmetrical U-shaped encoder–decoder structure, initially applied in medical image
taa sskysm. Tmhiestrmicoadl eUl-esmhapploeyds eannceondceord–edre–cdoedceord setrrsutcrtuucrteu,r einfiotriamllyu latip-spclaieledf eina tumreedfiucsailo nimaangde
segmentation tasks. This model employs an encoder–decoder structure for multi-scale fea-
psiexgeml-leenvtealticolans tsaisfikcsa.t Tiohnis, mwhodileelu etmilipzlionygs sakni penccoondneerc–tdioecnosdteora sctrquucitruersep faotri amluinltfio-srcmalaet ifoena-
ture fusion and pixel-level classification, while utilizing skip connections to acquire spatial
ftruorme ftuhseioenn caondde priaxnedl-laecvheile cvleasfseiafitcuarteiofnu,s wiohni.lTe huetilUiz-iNnget swkiaps ceoxntnenecdteiodnbsy toC ahceqnueirtea slp.[a4t1ia]l
information from the encoder and achieve feature fusion. The U-Net was extended by
tionpforrompoastieotnh efrRomec otnhset reuncctoiodnerB iaansdU a-cNheietvnee tfweaotrukr.eT fhuesyioand. dTehde thUe-NReeLt Uwafus necxttieonndaendd bay
Chen et al. [41] to propose the Reconstruction Bias U-Net network. They added the ReLU
mCahxepno eotl ianl.g [4la1y] etor apnrdopionstreo tdhue cReedcdonecstorduicntgiobnr Baniacsh Ues-Ninett hneetdweocorkd.e Trhtoeyc aapdtduerde tmheu lRtiepLleU
semanticinformationfromvariousupsamplingprocesses. Atpresent,thereisaprofusion
ofroadextractionmodelsbasedonencoder–decoderstructures, encompassingmodels
likeLinkNet,D-LinkNet[42],U-NetanditsvariantsVNet[43],U-Net++[44],U2-Net[45],

Sensors2024,24,1708 5of31
Dense-UNet [46], Res-UNet [47], MC-UNet [48], and others. While their structures ex-
hibitslightvariations,theprimarydistinctionslieintheencoderanddecoderbackbone
models, intermediatelayers, skipconnectionlayers, andnetworkmodeloptimizations.
Inrecentyears,therapiddevelopmentoftransferlearninghasfacilitatedmodeltraining,
especiallywhendealingwithlimitedtrainingdata,significantlyreducingtrainingtime
andcosts. Manyscholarsusenetworkmodelspre-trainedonImageNet,suchasVGG[49]
andResNet[50],asthebackbonestructurefortheirmodels. Forinstance,thepre-trained
VGG16fromImageNetwasintroducedbyDeepLabV1[51],alongwiththeproposalof
spatialconvolution(dilated/atrousconvolution)toincreasethereceptivefield,addressing
theissueofreducedresolutionduetorepeatedpoolinganddownsampling. ResNet-50was
adoptedasthebackbonestructureforPSPNet,whichintroducedspatialpyramidpooling
(SPP)togathercontextualinformationfromdifferentregions,therebyenhancingitsability
toobtainglobalinformation. DeepLabV2[52]replacedtheVGG16backboneofDeepLab
V1withResNet-101and,inspiredbySPP,introducedatrousspatialpyramidpooling(ASPP)
tointegratemulti-scaleinformation. TheemergenceofSPPandASPPresolvedtheissue
ofneedingtoresizeimagesbeforetheyentertheneuralnetwork,especiallyforfixed-size
inputslike224×224images. Atpresent,somescholarsintroduceSPPandASPPmodules
intomodelstoenhancetheextractionofroadfeaturesfromimagesthroughfeaturefusion.
Lan et al. [53] and Gao et al. [54] have respectively proposed the GC-DCNN and Tes-
LinkNetmodelsbasedontheU-NetandLinkNetmodels. TheformerintroducestheSPP
moduleintotheintermediatelayers,whilethelatterusestheASPPmodule.Huanetal.[55]
introducedtheSANetmodelpre-trainedwithResNet-50andintroducedtheASPPmodule
intheencoder. Inspiredbydenseconvolution,Q.Wuetal.[56]introducedthedenseand
globalspatialpyramidpoolingmodule(DGSPP)intothedecoderandencodertoenhance
thenetwork’sperceptionandaggregationofcontextualinformation. WeiandZhang[57]
integratedthemulti-levelstrippoolingmodule(MSPM)intotheskipconnectionlayers
toensureroadconnectivitybyaggregatinglong-rangedependenciesfromdifferentlevels.
LinkNetusedResNet-18astheencoderbackboneandimprovedsegmentationefficiencyby
directlyconnectingtheencoderanddecoder. D-LinkNetemployedthepre-trainedResNet-
34astheencoderbackboneandintroduceddilatedconvolutionsintheintermediatelayers.
The design of D-LinkNet includes four progressively larger dilated convolution layers,
formingastackedpyramidpattern,alsoknownastheD-Block,makingtheoutputofeach
layertheinputtothenext.Thisdesignexpandsthereceptivefieldwhilemaintainingimage
resolution,contributingtoitschampionshipintheDeepGlobe2018RoadExtractionChal-
lenge. However,thereisapotentialissuewiththedilatedconvolutionsintheintermediate
layersoftheD-LinkNetmodel,asitmayleadtothelossofcontinuousinformationbetween
neighboringpixelsandintroducesomeunrelatedcontextualinformation,affectingroad
extraction’sconnectivityandintegrity. Therefore,somescholarshaveenhancedthedilated
convolutionsintheintermediatelayersoftheD-LinkNetmodel. Gongetal.[58]replaced
dilatedconvolutionswithdensedilatedconvolutions,enablingmulti-scaleinformation
fusionwhileexpandingthereceptivefield. Wangetal.[59]restructuredtheD-Blockinto
the DP-Block, inspired by the pyramid attention network [60]. They introduced global
poolinganddesigneddenseconnectionsbetweenconvolutionstofullyutilizeglobaland
dense information for enhancing road features. J. Zhang et al. [61], on the other hand,
tookinspirationfromMobileNetV2[62]andintroducedbottleneckmodules(bottleneck
block)withintheD-Block,formingD-Blockplus,therebyreducingnetworkparametersand
improvingnetworkperformance.

SS enensosrosrs2 2002244,,2 244,,1 x7 0F8OR PEER REVIEW 6
6 o
o
f
f
3
3
1
2
FFigiguurree4 4..N NeettwwoorrkkM MooddeelslsB Baasseeddo onnE Ennccooddeerr––DDeeccooddeerrS Strturucctutureres.s.
2.2. RoadFeatureExtractionBasedonFeatureFusion
2.2. Road Feature Extraction Based on Feature Fusion
Featurefusionreferstothecombinationandsuperimpositionoffeaturesfromdifferent
Feature fusion refers to the combination and superimposition of features from differ-
layersorbranchesusingtechniquessuchasweightingorconcatenation. Thesefeatures
ent layers or branches using techniques such as weighting or concatenation. These fea-
possess distinct characteristics. Low-level features have higher resolution, containing
tures possess distinct characteristics. Low-level features have higher resolution, contain-
morepositionalanddetailedinformation,butduetofewerconvolutions,theirsemantic
ing more positional and detailed information, but due to fewer convolutions, their seman-
informationisrelativelylessandmaycontainsomelevelofnoise. High-levelfeatures,on
tic information is relatively less and may contain some level of noise. High-level features,
theotherhand,containrichersemanticinformationbuthavelowerresolutionandaless
on the other hand, contain richer semantic information but have lower resolution and a
effectiveabilitytoperceivedetailedinformation. Featurefusionemploysvariousstrategies,
less effective ability to perceive detailed information. Feature fusion employs various
such as feature concatenation, feature summation (including mean, pooling, weighted
strategies, such as feature concatenation, feature summation (including mean, pooling,
summation,likeASPPandSPPmentionedearlier),element-wisemultiplicationoffeature
weighted summation, like ASPP and SPP mentioned earlier), element-wise multiplication
elements,skipconnections,deconvolution,attentionmechanisms,andmulti-scalefeature
of feature elements, skip connections, deconvolution, attention mechanisms, and multi-
fusion. Thesemethodscomprehensivelyutilizefeaturesofdifferentlevelsandproperties,
scale feature fusion. These methods comprehensively utilize features of different levels
makingthemacrucialcomponentinnetworkmodels.
and properties, making them a crucial component in network models.
2.2.1. FeatureFusionBasedonAttentionMechanisms
2.2.1. Feature Fusion Based on Attention Mechanisms
Theattentionmechanismisacrucialmoduleindeeplearningnetworksandisconsid-
eredaTshaen aattdednittiioonna mlneecuhraanlinsemtw ios rak ctrhuacticaal nmeoffdeuctliev einly dineetepg lreaaternwinitgh nneetuwraolrnkest wanodr kiss [c6o3n].-
Isnidroeareddf eaast uarne aedxtdriatciotinoanl rneesueararcl hn,eistwsuoersks uthcaht acsafnr aegffmecetnivteedlye xintrteagctriaotne rwesituhlt sneaunrdalp onoert-
cwononrkesc t[i6v3it]y. Ionf treonada rfiesaetudruee etxotroabcsttirounc trieosnesarfcrhom, isbsuuielsd isnugcsh, tarse efsra,ogrmbeanctkegdr oeuxntrdacintitoenrf erre--
esnucletsw ainthds ipmoiolar rctoenxntuercetsi.vIintys uofcthenca aseriss,eb yduape ptroo porbisattreulyctiinotnros dfurocimng bautitlednitniogns,m troedeusl, eosr,
tbhaecmkgodroeulcnadn ifnotceursfemreonreceo nwiinthfo rsmimatiiloanr taetxrtouardese.d Igne ssuanchd cinatseerss,e bctyi oanpsp,rleoapdriinatgetlyo minotrroe-
cdouncniencgte adttaenndtiocnom mpoldetueleros,a dtheex mtraocdteiol ncarnes fuolctsu.s more on information at road edges and
interIsnerceticoennst,y leeaardsi,nagtt teon tmioonrem ceocnhnaencistemds ahnadv ecogmainpeledtec ornoasidd eerxatbralecttiroanc trioesnuilntst.h edomain
ofroaIdn erxetcreanctti oyne.arEsx, taettnseinvteiornes meaercchhahnaissmdesl vheadvein gtoaisneeldf- actotennsitdioenr,acbhlea ntrnaecltaiottne ninti otnhe[ 6d4o],-
smpaatiina loaf trtoeandti oenxt[r6a5c,t6io6n],. aEnxdtenhsyibvrei dreastetaerncthio hnasm deeclhvaendi simntso [s6e7lf]-.aTtthenetiionnte, gcrhaatnionnelo aftttehne-
mtiuonlt i[-6h4e]a, dspaatttieanl taiottnenmtieocnh [a6n5i,s6m6],f raonmd Thryabnrsidfo armtteenrti[o6n8] minetcohaarncihsmitesc [t6u7re].s Tlihkee iCntoengSrawtiionn-
Noef tth[6e9 m]aunldti-Sheega-dR oattaden[7ti0o]nh maseecfhfaecntiisvmel yfraodmd Trersasnesdfothrmeleirm [i6t8at]i ionntso oafrcchonitveectnutiroens alilkCeN CNons,-
mSwarikne-dNleyt e[6n9h]a anncdin Sgetgh-Reoaabdil i[t7y0t]o hpase recffeeivcteivreolayd atdedxrtuesrseeidn ttrhiec alicmieistaatniodncso onft ceoxntuvaelnitniofonra-l
mCaNtiNons,. mMaordkuedlelsyl eiknehtahnecisneglf -tahtet eanbtiiloitny fteoa ptuerrecetirvaen srfoeardm teoxdtuulree (iSnAtrFicMac)i[e7s1 a]nhda vcoenfuterxthtuearl
fiancfiolirtmateadtiocno.m Mporedhuelenss ilvikeei nthfoe rsmelaf-taiottnenintitoeng rfaetaitounrew tirtahninsfemr omdoedlsu,lseig (nSAifiFcMan)t l[y71b]o hlastveer ifnugr-
theperformanceandrobustnessofroadextractiontasks.
ther facilitated comprehensive information integration within models, significantly bol-
Thefoundationalmechanismsofthechannelattentionmodule(CAM)andspatial
stering the performance and robustness of road extraction tasks.
attentionmodule(SAM)playpivotalrolesinroadextraction. NetworkssuchasNested
The foundational mechanisms of the channel attention module (CAM) and spatial
SE-DeepLab[72]andRALC-Net[1]haveovercomechallengesinroadfeatureextractionby
attention module (SAM) play pivotal roles in road extraction. Networks such as Nested
leveragingthesqueeze-and-excitation(SE)andresidualattention(RA)modules. Addition-
SE-DeepLab [72] and RALC-Net [1] have overcome challenges in road feature extraction
ally,theincorporationofserialorparallelattentionmechanismsliketheconvolutionalblock
by leveraging the squeeze-and-excitation (SE) and residual attention (RA) modules. Addi-
attentionmodule(CBAM)[73]andProCBAM[74]markedlyimprovedthenetwork’sfocus
tionally, the incorporation of serial or parallel attention mechanisms like the convolutional
onroadinformation,therebyelevatingtheperformanceofroadextractiontasks. These
block attention module (CBAM) [73] and ProCBAM [74] markedly improved the net-
innovativemethodsandvariedapplicationsofattentionmechanismscomprehensively
work’s focus on road information, thereby elevating the performance of road extraction
showcaseeffectivestrategiesforenhancingmodelperformanceinroadextractiontasks,
tasks. These innovative methods and varied applications of attention mechanisms com-
enabling more efficient capture of road-related information. We have summarized the
prehensively showcase effective strategies for enhancing model performance in road ex-
prevalentattentionmechanismmodulesincurrentroadextractiontasksinTable1.
traction tasks, enabling more efficient capture of road-related information. We have sum-
marized the prevalent attention mechanism modules in current road extraction tasks in
Table 1.

Sensors2024,24,1708 7of31
Table1.AttentionMechanismsandMethods.
Model/Method AttentionMechanism Highlight(s)/Strength(s)
IntroductionofdualSwin
Transformersandaresidualblock
withintheU-Netnetworkstructure,
creatingtheConSwin-Net,which
ConSwin-Net[69] Multi-HeadSelf-Attention mitigatesCNNlimitationsin
extractingglobalcontextualfeatures,
therebyenhancingthemodel’s
perceptionofroadtexturedetailsand
globalinformation
IncorporationofaTransformer
structureintotheencodercombined
withaconvolutionalneuralnetwork
Seg-Road[70] Self-Attention (CNN)decoderleadstoimproved
connectivityinroadsegmentation
andenhancedprediction
resultrobustness
Integrationoftheself-attention
featuretransfermodule(SAFM)into
thehiddenlayersofconvolutional
neuralnetworksestablishes
relationshipsbetweeneachhidden
FSNet[71] Self-Attention layeranditscontextualhiddenlayers.
Thisfacilitatesthetransferofhidden
layerfeatureinformationto
theoriginalfeaturemap,
resultinginimprovedroad
extractionperformance
IntroductionofSEmoduleintothe
encoderanddecodereffectively
NestedSE-DeepLab mergesandretainsbothshallowand
ChannelAttention(SE)
network[72] deepinformation,addressingmodel
imbalanceissuesinnarrow
roadextraction
IntegrationoftheSEmoduleintothe
encoderoftheD-LinkNetnetwork
DSDNet[29] ChannelAttention(SE)
assistsResNetinfeatureextraction
formountainroads
CombiningtheSEmodulewiththe
ASPPmoduleduringdownsampling
TSE-LinkNet[54] ChannelAttention(SE) enhancestopologicalrelationships
betweenadjacentroadpixels
inimages
UtilizationoftheimprovedMECA
ModifiedEfficientChannel moduleenhancesthecontinuityof
BMDANet[75]
Attention(MECA) roadfeaturesbasedonthe
characteristicsofRSIroads
ConstructionofanMSACon
dual-encodernetworkwithaspatial
attention-basedfusion(SAF)
MSACon[76] SpatialAttention(SAM)
mechanismimprovesroadextraction
byutilizingcontextualrelationships
betweenroadsandbuildings

Sensors2024,24,1708
8of31
Table1.Cont.
| Model/Method | AttentionMechanism | Highlight(s)/Strength(s) |
| ------------ | ------------------ | ------------------------ |
Developmentofadual-encoder
RALC-Netnetworkwitharesidual
attention(RA)moduleintegrates
| RALC-Net[1] | SpatialAttention(SAM) |     |
| ----------- | --------------------- | --- |
spatialcontextualinformationto
emphasizelocalsemantics,aidingin
theextractionoflocalroadfeatures
| GCB-Net[28], |                     | Focusingonhighlightinghigh-level |
| ------------ | ------------------- | -------------------------------- |
| CDG[77],     | GlobalAttention(GA) | roadfeaturestoimprove            |
| CADUNet[78]  |                     | segmentationresults              |
Ensuringthemaximumtransmission
ofroadinformationbetweendense
CADUNet[78] CoreAttention(CA) blocksandcoordinatingmulti-scale
roadinformationacquisitionthrough
theglobalattentionmodule
Facilitatingthefusionoflower-level
| SANet[55] | StripAttention(SAM) |     |
| --------- | ------------------- | --- |
andhigher-levelroadfeatures
Enhancingpixel-levelrepresentation
capabilitiesbycapturinglong-range
| FE-LinkNet[59] | Criss-CrossAttention(CCA) |     |
| -------------- | ------------------------- | --- |
contextualinformationinhorizontal
andverticaldirections
Improvingnetworkfocusonimages
ConvolutionalBlock
| SegRExt-F[67] |     | throughconcatenationofchanneland |
| ------------- | --- | -------------------------------- |
AttentionModule(CBAM)
spatialattentionusingCBAM
Enhancingtheintegrationofroad
ProConvolutionalBlock
| DU-Net[74] |     | informationthroughProCBAMwith |
| ---------- | --- | ----------------------------- |
AttentionModule(ProCBAM)
addedSEmodule
Introducingthepositionattention
module(PAM)andglobal
PositionAttentionModule
| SDG-LinkNet[61] |     | informationrecoverymodule(GIRM) |
| --------------- | --- | ------------------------------- |
(PAM)withD-Blockplus
inparallelforglobal
informationacquisition
Designedtoalleviateroadocclusion
|     | Long-RangeContext-Aware | issuesbyacquiringlong-range |
| --- | ----------------------- | --------------------------- |
Meca-Net[66]
|     | Module(LCAM) | contextinformationthroughchannel |
| --- | ------------ | -------------------------------- |
andspatialattention
Enhancingroadinformation
GAN[79],
extractionandsegmentation
| MAU-Net[80], | ParallelChanneland |     |
| ------------ | ------------------ | --- |
performancethroughtheintegration
| GAMSNet[81], | SpatialAttention |     |
| ------------ | ---------------- | --- |
ofparallelchanneland
CM-FCN[82]
spatialattention
|             | FeatureFusionbased | Introducedafeaturefusion         |
| ----------- | ------------------ | -------------------------------- |
| MAU-Net[80] | onAttention        | mechanism(FFBAM)forbetterfitting |
|             | Mechanism(FFBAM)   | multi-scaleroadinformation       |
IntroducedBMDAforfeature
BlockMulti-Dimensional
| BMDANet[75] |     | extractioninblocks,integratingthem |
| ----------- | --- | ---------------------------------- |
Attention(BMDA)Module
throughchannelandspatialattention

Sensors2024,24,1708 9of31
Table1.Cont.
Model/Method AttentionMechanism Highlight(s)/Strength(s)
Coarsefeatureextractionwithdilated
CascadedMulti-Scale
convolutionpooling,followedby
CMAFE[83] AttentionFeature
boundaryenhancementinthe
Enhancement(CMAFE)
lightweightU-Netnetwork
IntroducedRse-Netwithmulti-scale
convolutionalattentionmodule,
Multi-ScaleConvolutional
Rse-Net[84] focusingonboundaryinformation
AttentionModule(CSAM)
andexpandingthereceptivefieldfor
moresemanticinformation
2.2.2. FeatureFusionBasedonMulti-ScaleImages
Theterm“multi-scale”referstoimagesofdifferentresolutionsordifferentlevelsof
imagefeatures(low-levelfeatures,high-levelfeatures). Thepurposeoffeaturefusionisto
explorehowtoeffectivelyutilizethesemulti-scaleimagestoobtainmoreaccurateroad
featureinformation[85].
Thedesignofmulti-scalefeaturefusionmodulesoftendrawsinspirationfromparallel
orserialmulti-branchnetworkarchitectures,suchasfeaturepyramidnetworks(FPNs)[86],
Inception[87],andHRNet[88].Thissectionprovidesanoverviewofthemulti-scalefeature
fusionmodulesandmethodsemployedinroadimagesegmentationtasks. Researchers
haveutilizedsupervisedlearningbycombiningedgeinformationwithimagefeaturesto
enhanceroadimagesegmentationnetworks. Variousmoduledesignshavebeenproposed
toaddressissuesrelatedtoextractingroadshapesandenhancingconnectivity,suchasthe
multi-scalecontextaugmentationmodule[89],spatialcontextmodule[90],andfeature
review module [91]. Some modules are particularly adept at capturing elongated road
shapes, while others focus on enhancing global features. Additional modules aim for
multi-scalefeaturefusion. Solutionstailoredfornarrow,continuous,andexpansiveroads
inhigh-resolutionremotesensingimageshavealsobeenproposed,incorporatingmultiple
modulestooptimizespatialfeaturepreservation,shapeenhancement,andmulti-feature
fusion. Theseinnovativemodulesandmethodscollectivelydriveadvancementsinroad
extractiontasks,providingcrucialtechnicalsupportformoreaccurateidentificationofroad
shapesandimprovedsegmentationoutcomes. Duetospacelimitations,detailedmethod
characteristicsaresummarizedinTable2.
Table2.Multi-ScaleFeatureFusionModuleandMethods.
Multi-ScaleFeature
Model/Method Highlight(s)/Strength(s)
FusionModule
Enhancingroadextraction
Geographic connectivitythroughjointlearningof
JointSharedLearning
Feature-Enhanced pixel-level,edge-level,and
andFeatureFusion
Network[92] region-levelroadfeatures,followed
byfeaturefusion
Enlargingthereceptivefieldand
Multi-ScaleContext
DA-CapsUNet[89] integrationofcontextinformation
Augmentation(CTA)
fromdifferentscales
CoarseMapPredicting Seriallyconnectedspatialcontext
BT-RoadNet[90] Module(CMPM)and moduleeffectivelycaptures
SpatialContextModule elongatedroadshapes

Sensors2024,24,1708 10of31
Table2.Cont.
Multi-ScaleFeature
Model/Method Highlight(s)/Strength(s)
FusionModule
Evaluatingroadfeaturesofvarying
scales,withanemphasisoncontour
DeepFRTransNet[91] FeatureReview(FR)
characteristics,toimproveroad
profileinformation
Aligningfeaturemapsacrossscalesto
extracthigh-frequencyinformation,
DiscriminativeContext-Aware
DCANet[93] witharefinedecoder(RD)forspatial
Feature(DCF)Module
informationretentionand
featurerepresentation
Recursiveintegrationoffeaturesfrom
twopathways,leveragingscale
All-ScaleFeatureFusion(AF) featureswithvaryingspatialand
AF-Net[94]
Module semanticinformation,toprovide
accuratespatialandsemantic
informationforroadextraction
Improvedsemanticinformationof
GlobalFeatureRefinement
NFSNet[71] featuremapsformoredetailed
(GFR)Module
segmentationoutputs
Enhancedandseparatetransmission
Feature-EnhancedConnection
ofstructuralandtexturalfeaturesto
ConSwin-Net[69] (FC)andShape-Augmented
thedecoder,improvingoverall
Connection(SC)
modelperformance
UtilizingtheHoughtransform(HT)
Multi-ScaleLineEnhancement
MLEM-NET[95] toenhancelocalandgloballinear
Module(MLEM)
featuresinremotesensingimages
Constructingspatialrelationships
DenselyConnectedEncoder betweenfeaturesatdifferent
SDUNet[96] BlockandSpatialIntensifier positionsandintroducingskip
(DULR)Module connectionlayerstopreservethe
topologicalstructure
Utilizingconvolutionkernelsof
differentscalesizesandaggregating
Multi-ScaleFeatureEncoding
Meca-Net[66] multi-scalefeaturesthroughaparallel
Module(MFEM)
strategyforrecognizing
elongatedroads
Extractingandmergingfeaturesfrom
FeatureEnhancementModule
MSPFE-Net[57] variouslevelstoaccomplish
(FEM)withStripePooling
multi-scalefeaturefusion
Expandingandmergingfeaturesto
FeatureExpansionModule addresschallengesposedbynarrow
LDANet[97] andDeepFeatureAssociation andcomplexruralroads,improving
Module featureassociations,andpromoting
multi-featurefusion
Improvingroadimagesegmentation
MTMF[98] CannyOperatorandHRNet throughthefusionofedge
informationandimagefeatures
2.2.3. FeatureFusionBasedonMulti-ModalFusion
Solelyrelyingonopticalremotesensingimagerytoprovidelearninginformationfor
networkmodelsdoesnotguaranteeexcellentlearningoutcomes. Thisisduetospectral
similaritiesbetweenbuildingsandroadsandthepotentialforocclusionscausedbytall
buildingsandtrees. Thesefactorscanleadtoinaccurateidentificationandacquisitionof

Sensors2024,24,1708 11of31
roadfeatureinformationbythemodel,ultimatelyaffectingroadextractionresults. Addi-
tionally,sensorimagingandlightingconditionscanalsoadverselyaffecttherecognition
andacquisitionofroadfeatureinformation. Recognizingthischallenge,researchershave
exploredmulti-modaldata,includingmulti-spectral(hyperspectral)data,syntheticaper-
tureradar(SAR)[99],lightdetectionandranging(LiDAR),unmannedaerialvehicle(UAV)
data,GPStrajectorydata,andmulti-temporaldata. Thepenetrativeandobliqueobserva-
tionpropertiesofsyntheticapertureradar(SAR)havebeeningeniouslyleveragedbyJ.
Zhangetal.[61]toaddressissuesarisingfromshadowsandocclusionscausedbyvegeta-
tionandbuildingsinopticalremotesensing,providingnetworkmodelswithmoredetailed
roadinformation. Ontheotherhand,dual-temporalopticalremotesensingimageryhas
beenemployed[100]todetectandupdateroaddatabases. Sensorswithhighrevisittimes,
suchasSentinel-1andSentinel-2,havebeenutilizedbyAyalaetal.[28]toenhancedatasets
withmulti-temporalmulti-spectralandSARdatathroughcolordataaugmentation.
Multi-modalfusioninvolvesfeatureintegrationbetweendifferentdatasources,par-
ticularlyforcross-sourcefusionbetweenGPStrajectorydataandremotesensingimagery.
Similarly, we have provided a more intuitive tabular summary of methods related to
multi-modalfeaturefusioninTable3.
Table3.Multi-modalFusionModuleandMethods.
Model/Method ModuleName FusionDataSources Highlight(s)/Strength(s)
GFMwasdesignedtocontroland
GPStrajectorydataand integrateinformationfromboth
DeepDualMapper[101] GatedFusionModule(GFM)
remotesensingimagery modalitiesinacomplementary
perceptionmanner
AFMwasutilizedtointegrateroad
AdaptiveFusion GPStrajectorydataand
MTMSAF[102] featuresfromtrajectorydataand
Module(AFM) remotesensingimagery
remotesensingimagery
DEMwasintroducedtoenhance
andcomplementfeaturesfromboth
DualEnhancement Cross-sourcefusionof imagesandtrajectorydata
CMMPNet[103]
Module(DEM) imagesandtrajectorydata bidirectionally,applicablefor
LiDARandremotesensing
imagerydata
Hyperspectralandremotesensing
imageryarecombinedtoalleviate
Traditionalremotesensing
Cross-sourceFeatureFusion discontinuousoutputsandusing
MSFANet[104] imageryand
Module(CFFM) CFFMtocorrectandfusespectral
hyperspectralimagery
featuresatdifferentscales,reducing
noiseandredundancy
Attention mechanisms themselves are models with advantages such as fewer pa-
rameters,fasterprocessingspeed,andgoodperformance. ComparedtoCNNs,attention
mechanismshavelowermodelcomplexity,fewerparameters,andlowercomputational
requirements. Furthermore,attentionmechanismsaddresstheissueofnon-parallelcom-
putationinRNNs[105],astheydonotrelyontheresultsofthepreviousstep,enabling
efficientparallelcomputation.Hence,theyhavebecomeanimportantcomponentoffeature
fusioninnetworkmodels. However,itisworthnotingthattheintroductionofattention
mechanismsmayleadtomodeloverfitting. Ifanetworkmodelisalreadycomplex,incor-
poratingattentionmechanismscanincreasethenumberofmodelparameters,potentially
causingoverfittingissues. Additionally,fusingdifferentfeaturestogethermayintroduce
noiseandotherchallenges. Attentionitselfisatypeoffeature,sowhenintegratingitwith
otherfeatures,carefulconsiderationisneededtoassesswhetheritmightnegativelyimpact
thenetworkmodel’sperformance. Formulti-modaldata,whileitprovidesrichersemantic
informationtonetworks,theremaybedifferencesinsemanticsamongdifferentmodalities.

Sensors2024,24,1708 12of31
Therefore,addressingnoisereductionandsemanticdifferenceswhilefusingthesefeatures
isanissuetobefocusedoninthefuture.
2.3. RoadFeatureExtractionBasedonGANs
In2014,generativeadversarialnetworks(GANs)wereintroducedbyGoodfellowetal.[106]
operatingonanunsupervisedlearningapproach,consistingofageneratorGandadis-
criminatorD.Thetaskofthegeneratoristogeneratedatacloselyresemblingrealimages,
attemptingto“deceive”thediscriminator. Thediscriminator’sroleistodeterminewhether
thedatageneratedbythegeneratoriscorrectandprovidefeedbacktoenhancethegenera-
Sensors 2024, 24, x FOR PEER REVIEW 13 of 32
tor’sabilityto“fabricate”. Thisprocessformsacycle,continuinguntilneithercandeceive
the other. Essentially, it is a zero-sum game, also known as the Bash game. However,
becausethegeneratordoesnotrequiretraininglabels,datacanbegeneratedtoofreely,
iinmclaugdein rgecimogangietsi,otnex tta,sokrse.v Teon asodudnrdesfsr otmhisn iosissue,ew, thhiceh inistrnoodtuidcetaiolnfo orfi msoamgeer ceocongdniittiioonns to both
ttahsek sg.eTnoeraadtdorre assndth disisiscsruime,itnhaetoinr twroadsu pctrioonpoosfesdo.m Ine cthoen dciotinotnesxtt oofb oimthatghee rgeecnoegrnatiotiron tasks,
and discriminator was proposed. In the context of image recognition tasks, conditions
conditions could be introduced to the discriminator to make it generate only images. In
couldbeintroducedtothediscriminatortomakeitgenerateonlyimages. Inthesameyear,
the same year, conditional generative adversarial networks (CGANs) [107] were introduced
conditionalgenerativeadversarialnetworks(CGANs)[107]wereintroduced(Figure5).
(Figure 5). CGANs are generative adversarial network models with constraint conditions.
CGANsaregenerativeadversarialnetworkmodelswithconstraintconditions. Incorporat-
Incorporating variables y into both the generator and discriminator, these variables guide
ingvariablesyintoboththegeneratoranddiscriminator,thesevariablesguidethedata
the data generation process by the generator. The variables y can be labels or even images,
generationprocessbythegenerator. Thevariablesycanbelabelsorevenimages,marking
amsahrifktionfgG aA sNhisftf roofm GuAnNsusp ferrovmise udnlseuarpneinrvgistoewd alerdasrnsiunpge rtvoiwseadrdlesa rsnuipnegr.vised learning.
FFiigguurere5 .5N. NetewtworokrMk oMdoeldBeal sBeadsoend Coonn CdiotinodniatlioGneanle rGaetinveerAatdivveer Asadrivale.rsarial.
In2017,thePix2pix[108]modelwasintroduced,whichisbasedonthestructureof
In 2017, the Pix2pix [108] model was introduced, which is based on the structure of
conditionalgenerativeadversarialnetworks(CGAN)forimage-to-imagetransformations,
conditional generative adversarial networks (CGAN) for image-to-image transfor-
alsoreferredtoasdomainadaptation. Inthisapproach,thegeneratorofthemodelutilizes
amUa-tNioentsn, eatwlsoor kre,fwehrrieledt hteo daiss cdriomminaaitno raidsadpetsaigtinoend. uInsi ntghitsh eapPpatrcohaGcAh,N thaerc hgietencetruarteo.r of the
Mmaondyerl eusteialirzchese ras Uco-nNtientu neettowroerfekr,e wncheilteh itshme dodiseclriinmciunrarteonrt irso dadeseixgtnraecdt iuonsintags kths.eF PoartchGAN
ianrsctahnitceec,tYuarneg. aMndanWya rnegs[e1a0r9c]hfoelrlso wcoendttihneuset rtuoc rtuerfeeroefnPcixe2 tphiixsa mndodinetrl oindu ccuerdrethnet WroGaAd Nex-traction
GtaPsknse.t wFoorr kinfsotrarnucrea,l Yroaandg eaxntdra Wctiaonng. T[1h0e9y]u fsoeldlobwoethd Uth-Ne settrauncdtuBrieS eoNf Petixa2spgiexn aenradto irnst,roduced
employinganensemblestrategytocombinetheirinferenceoutputsforbetterroadvector
the WGAN-GP network for rural road extraction. They used both U-Net and BiSeNet as
generation. ThediscriminatorintheirmodelusedPatchGAN.Ciraetal.[110,111]applied
generators, employing an ensemble strategy to combine their inference outputs for better
thePix2pixmodeltopost-processroadextraction. Theyimprovedtheintegrityofroad
road vector generation. The discriminator in their model used PatchGAN. Cira et al.
surface area extraction by contaminating labels and reconstructing them. In addition,
[110,111] applied the Pix2pix model to post-process road extraction. They improved the
Abdollahietal.[7]proposedadeeplearningapproachusingconditionalgenerativeadver-
sianrtieaglrnietytw oofr rkosa(dC GsuArNfasc)ef oarrerao aedxtsreagcmtieonnt abtyio cnoinnthamighin-raetsionlgu tliaobnealse rainaldi mreacgoenrsy.trTuhcetying them.
uInti laizdeddiatinonen, hAabndceodllaUh-Ni eett aml.o [d7e]l p(MroUpNoseetd)a as daegeepn elreaatronritnogs eagpmperonatcimh augseisnagn cdoonbdtiatiinonal gen-
heirgaht-irvees oalduvtieornsasergiaml ennettewdomrkaps s(CofGrAoaNdsn)e ftowro rrokas.dN sIeGgAmNen[1ta1t2i]o,nco imn phriigshin-gretswooluCtGioAnN aerial im-
naegtewroyr.k Ts,hweya suutisleidzefdor asnce ennehsaenleccetido nUi-nNmeot umnotadineol u(MsrUoaNdestc)e ansa rai ogse.nTehriastwora stoca sreiegdmoeuntt images
topre-selectareasthatcontainmountainousroadscenes,therebyreducingtheworkload
and obtain high-resolution segmented maps of road networks. NIGAN [112], comprising
two CGAN networks, was used for scene selection in mountainous road scenarios. This
was caried out to pre-select areas that contain mountainous road scenes, thereby reducing
the workload in subsequent segmentation and road extraction tasks. The generator in their
model is based on an encoder–decoder structure, utilizing ResNet-34 as the backbone. Mid-
dle layers incorporate dilated convolutions, which are helpful for extracting small objects
like roads and expanding the receptive field while enhancing global information.
Conditional generative adversarial networks (CGANs) have played a crucial role in
road extraction tasks. They are not only used for road segmentation but also for pre-pro-
cessing road extraction, enriching road information in images, and reducing the workload
for subsequent segmentation networks. Additionally, in post-processing, employing ad-
versarial training techniques to enhance segmentation results has reduced issues related
to fragmentation while improving road connectivity.
2.4. Road Feature Extraction Based on Cumulative Integration of Multiple Models

Sensors2024,24,1708 13of31
in subsequent segmentation and road extraction tasks. The generator in their model is
basedonanencoder–decoderstructure,utilizingResNet-34asthebackbone. Middlelayers
incorporatedilatedconvolutions,whicharehelpfulforextractingsmallobjectslikeroads
andexpandingthereceptivefieldwhileenhancingglobalinformation.
Conditional generative adversarial networks (CGANs) have played a crucial role
inroadextractiontasks. Theyarenotonlyusedforroadsegmentationbutalsoforpre-
processingroadextraction,enrichingroadinformationinimages,andreducingthework-
loadforsubsequentsegmentationnetworks. Additionally,inpost-processing,employing
adversarialtrainingtechniquestoenhancesegmentationresultshasreducedissuesrelated
tofragmentationwhileimprovingroadconnectivity.
2.4. RoadFeatureExtractionBasedonCumulativeIntegrationofMultipleModels
Inroadextractiontasks,ensemblestrategieshavebeenincreasinglyadoptedbyre-
searcherstocombinemultiplemodelsseriallyorinparallel. Integratedmodelswithstrong
generalizationcapabilities,highrobustness,andexceptionalsegmentationperformance
havebeenhighlysoughtafterinresearchendeavors. Parallelstrategies(Figure6)aremost
commonlyused. Forexample,Senthilnathetal.[113]employedthreerelativelymature
networkmodels,FCN-32,Pix2Pix,andCycleGAN[114],fortransferlearning. BothPix2Pix
andCycleGANarecommonlyusedindomaintransfertasks. Thekeydifferenceisthat
Pix2Pixrequirestrainingdatatobeinpairs, whichischallengingtofindinthenatural
world. TheemergenceofCycleGANeffectivelysolvesthisproblem. Theyproposedthe
DeepTECintegratedclassifier,whichutilizesaparallelstrategytointegratetheresultsof
roadsegmentationfromthreemodels. Thisapproachachievedoutstandingintegration
performanceinextractingurbanroadnetworksfromdrones. Ciraetal.[115]combined
improvedCNN,VGG,ResNet-50,andInception-ResNet[116]modelsinparallelandfused
extractionresultsusinganaveragingstructure. Thisstrategyaimstoleveragethestrengths
ofeachmodelwhileminimizingtheirweaknesses,ultimatelyresultinginaclassifierwith
reducedclassificationerror. Chenetal.[117]employedResNet-50modelswiththreedis-
tinctconvolutionkernelsizesforroadextraction,integratingtheresultstoformaResNet-50
trainingblockenrichedwithhigh-levelinformation. Lietal.[118]reorganizedthelayers
ofU-NetandduplicatedasinglesubmodelNtimes,creatinganensemblemodelEcon-
sistingofNparallelsubmodels. Followingoptimizationandprediction,theyultimately
established an E-UNet model with 14 layers. Abdollahi et al. [119] adopted a parallel
approachbylinkingtwoimprovedU-Netmodels,BCL-UNet(ConvLSTM[120]+U-Net)
andMCG-UNet(BConvLSTM+SE+denseconvolutions[121]). Theyintroduceddense
convolutionsandcompressionactivationmodulesintheupsamplinglayersofthestandard
U-Net. Theyemployedbidirectionalconvolutionallongshort-termmemory(BConvLSTM)
forskipconnections,enablingthegenerationofhigh-resolutionsegmentationmapseven
inchallengingbackgroundswhilepreservingedgeinformation. Thegraph-baseddual
convolutionalnetwork(GDCNet)[122]integratesgraphconvolutionalnetworks(GCNs)
and CNNs. Employing a ResNet-50 backbone that included encoder and decoder con-
volutionalneuralnetworks,researchersappliedaparallelapproachforroadextraction,
effectivelyaddressingconcernsassociatedwithpoorconnectivityanddiscontinuities. This
wasachievedbygeneratingcomplementaryspatial–spectralfeaturesatbothsuperpixel
andpixellevelsandefficientlypropagatingthesefeaturesbetweengraphnodesandimage
pixelsusingagraphdecoder. Sunetal.[123]employedaparallelnetworkmodelconsisting
of dual branches for road and building extraction. One branch is the multi-resolution
semanticextractionbranch,composedofthreeparallelResNetnetworks,usedtoextract
semanticfeaturesofroadsandbuildingsatdifferentresolutions. Theotherbranchisthe
Transformersemanticextractionbranch,whichutilizesaResNet-18backboneandfeatures
aTransformer-basedencoder–decoder. Thisparallelstrategysuccessfullyaddressesthe
currentlimitationofsemanticsegmentationnetworksintermsofreceptivefieldbyfusing
theoutputresultsofthetwobranches.

Sensors 2024, 24, x FOR PEER REVIEW 15 of 32
Sensors2024,24,1708 14of31
Figure6.NetworkModelBasedonCumulativeIntegrationofMultipleModels.
Figure 6. Network Model Based on Cumulative Integration of Multiple Models.
Certainly, a serial strategy employing multiple models for road extraction is also
utilized by some researchers. For instance, a direction-aware residual network, DiRes-
NWeti[t1h2 4t]h.eD ciRoenstNineutcooumsp driesveselaoRpemsNeentts oegf mdeenetpa tlieoanrnneitnwgo, rmk(oDdiReless Saerge) gbraasedduoanlltyh eevolving to-
warddesc godreinagtelra ydeerspwthit hanstdru wctiudrtahl.s uHpoerwviesvioenr,a intd isa irmefipnoemrteannttn teot wnoortke (tDhiaRte isnRcerf)ebaassinedg depth and
onU-Net. Theformerisdedicatedtoenhancingthelearningofroadtopology,whilethe
width does not always lead to improved model performance and can potentially result in
latterfurtherrefinestheroadsegmentationresults. Z.Chenetal.[125]drewinspiration
issues like overfitting. In this section, we summarize how scholars leverage the unique char-
from the AdaBoost classification algorithm and combined multiple lightweight U-Net
actemrisotdieclss boyf cdoinfnfeercetinngt tmheomdienlsa asenrdia lemmanpnloery, foernmsienmgbAldea Bstoroastte-lgikieese ntdo- toin-etnedgrmautelt itphleese models.
Theslieg hcthwaeriagchtteUri-sNtiectss (iAncElMuLdeU h-Naevtisn).gU fnedweerrth misosedreial lpsatrraatemgye,ttehres,o fuatpstu rteocfothgenpitrieovnio supseed, strong
networkservesastheinputforthenextone. ToensurethetrainingqualityofeachU-Net,
generalization, and expertise in extracting road features in various scenarios. By combining
theresearchersdesignedamulti-objectiveoptimizationstrategyforjointtrainingofall
multiple models, whether they are simple or mature, researchers have achieved better road
U-Nets. Finally, the output results of each U-Net are fused to obtain the ultimate road
featuexrter aecxtitornacretisounlt. results than with a single model. Nonetheless, it is essential to be aware
that muWltiipthlet hiencdoenptiennudouesndt emveolodpemlse ndtoo fndoete pallweaarnyisn go,umtpodereflsoarmre gar addeueapllyere vaonlvdi nlgarger single
towardsgreaterdepthandwidth. However,itisimportanttonotethatincreasingdepth
model. This is because these models are trained independently, and their training outcomes
and width does not always lead to improved model performance and can potentially
may vary. In parallel extraction, individual models may perform poorly, becoming bottle-
resultinissueslikeoverfitting. Inthissection,wesummarizehowscholarsleveragethe
necks for overall performance. In serial extraction, if the same model is used for serial pro-
uniquecharacteristicsofdifferentmodelsandemployensemblestrategiestointegratethese
cessminogd, eilts .mTahyes leecahda rtaoc tae rsisetriciessin ocflu pdreohbalveimngs.f eFwoerr imnsotdaenlcpea,r admeteetermrs,infaisntgre sctorgantietigoines to ensure
conssipseteedn,ts ttrroaningignegn erreasliuzalttiso nfo,ar nedaecxhp emrtoisdeeinl aexntdra cwtinhgetrhoaedr faenat uerxecseinssvivareio nuusmscebnearr ioosf. models ef-
By combining multiple models, whether they are simple or mature, researchers have
fectively deepens the model’s depth, potentially leading to gradually declining perfor-
achievedbetterroadfeatureextractionresultsthanwithasinglemodel. Nonetheless,itis
mance. These issues are worthy of in-depth consideration and exploration.
essentialtobeawarethatmultipleindependentmodelsdonotalwaysoutperformadeeper
andlargersinglemodel. Thisisbecausethesemodelsaretrainedindependently,andtheir
2.5. tRraoiandin Fgeoauttucroem Eesxmtraayctvioanry .BIanspeadr aolnle lMexutlrtaicptiloe nT,ainsdksiv idualmodelsmayperformpoorly,
becomingbottlenecksforoverallperformance. Inserialextraction,ifthesamemodelis
The focus of most current road extraction tasks is primarily on extracting road
usedforserialprocessing,itmayleadtoaseriesofproblems. Forinstance,determining
surfsatrcaetseg. iHesotwoeenvseurr,e rcooandsisst eenntctoraminpinagssre vsualrtisofuors eealcehmmeondtesl, ainndclwuhdeitnhger raonaedx cceesnsitveerlines, road
edgensu,m rboeardo fnmooddeesl,s aefnfedc tmiveolryed, eaelpl eonfs wthehimchod aerl’es deeqputha,llpyo tiemntpiaollrytalenatd.i nCgotnosgerqaduueanlltyly, the chal-
decliningperformance. Theseissuesareworthyofin-depthconsiderationandexploration.
lenge of achieving multi-task road extraction persists. Many researchers are exploring net-
work models for accomplishing multi-task road extraction in remote sensing images, sur-
2.5. RoadFeatureExtractionBasedonMultipleTasks
passing the scope of surface extraction alone (Figure 7).
Thefocusofmostcurrentroadextractiontasksisprimarilyonextractingroadsurfaces.
However,roadsencompassvariouselements,includingroadcenterlines,roadedges,road
nodes, and more, all of which are equally important. Consequently, the challenge of
Figure 7. Network Models Based on Multiple tasks.

Sensors 2024, 24, x FOR PEER REVIEW 15 of 32
Figure 6. Network Model Based on Cumulative Integration of Multiple Models.
With the continuous development of deep learning, models are gradually evolving to-
wards greater depth and width. However, it is important to note that increasing depth and
width does not always lead to improved model performance and can potentially result in
issues like overfitting. In this section, we summarize how scholars leverage the unique char-
acteristics of different models and employ ensemble strategies to integrate these models.
These characteristics include having fewer model parameters, fast recognition speed, strong
generalization, and expertise in extracting road features in various scenarios. By combining
multiple models, whether they are simple or mature, researchers have achieved better road
feature extraction results than with a single model. Nonetheless, it is essential to be aware
that multiple independent models do not always outperform a deeper and larger single
model. This is because these models are trained independently, and their training outcomes
may vary. In parallel extraction, individual models may perform poorly, becoming bottle-
necks for overall performance. In serial extraction, if the same model is used for serial pro-
cessing, it may lead to a series of problems. For instance, determining strategies to ensure
consistent training results for each model and whether an excessive number of models ef-
fectively deepens the model’s depth, potentially leading to gradually declining perfor-
mance. These issues are worthy of in-depth consideration and exploration.
2.5. Road Feature Extraction Based on Multiple Tasks
The focus of most current road extraction tasks is primarily on extracting road
Sensors2024,24,1708 surfaces. However, roads encompass various elements, including road cen 15 te o r f l 3 i 1 nes, road
edges, road nodes, and more, all of which are equally important. Consequently, the chal-
lenge of achieving multi-task road extraction persists. Many researchers are exploring net-
awchoierkv imngomdeullst if-otars akcrcooamdpelxitsrhaicntigo nmpuelrtsi-itsatss.kM roaandy erexsteraarccthioenrs inar reeemxpoltoer sinegnsnientgw iomrkages, sur-
mpoadseslisnfgo rthaec csocmopplei sohfi nsgumrfaucltei- etaxstkraroctaidonex atrloacnteio (nFiingurerme o7t)e. sensingimages,surpassing
thescopeofsurfaceextractionalone(Figure7).
FFigiguurere7 .7N. NetwetowrkorMk oMdeoldseBlass eBdasoendM ounl tMipulelttiapskles .tasks.
In the road surface and centerline extraction tasks, the D-LinkNet model was em-
ployed [126]. Initially, the imagery was coarsely segmented for road extraction. Subse-
quently, the boosting segmentation network (BSNet) based on the ResNet-34 network
architecturewasusedtoenhancetheconnectivityandaccuracyofthecoarsesegmentation
results. Roadintersectionssimultaneouslygeneratedstartingpointsbyemployingmulti-
start point tracking. Finally, an iterative search strategy embedded with convolutional
neural networks (CNNs) was used to track a continuous and complete road network.
Refinedextractionofroadsurfacesandcenterlineswasachievedbyintegratingsegmenta-
tion,trackingresults,semanticinformation,andtopologicaldata. Adual-taskend-to-end
convolutionalneuralnetwork(MRENet)[127]withadual-branchstructurewasdeveloped.
Thesetwobranchesfacilitatedfeaturesharing,withthemainbranchresponsibleforroad
surfaceextraction,andtheotherbranchutilizingfeaturesextractedfromthemainbranch
asconditionsforcenterlineextraction. Thisinformationexchangeandparametersharing
approachhelpedmitigatepotentialissuesarisingfrominsufficientcenterlinesamples. To
addresstheproblemofpoorconnectivityinroadextractionoftencausedbycomplexback-
grounds,Luetal.[128]identifiedinterconnectionsbetweendifferentextractiontasks. For
example,theroadsurfacesegmentationresultsinfluencedthefinalpositionofcenterlines
andedges,andtheintegrityofroadedgeswascloselyrelatedtoroadsurfaceconnectivity.
Therefore, theyproposedacascadedmulti-task(CasMT)roadextractionframeworkto
simultaneouslyextractroadsurfaces,centerlines,andedges. Thisframeworkfullylever-
agedtheinterrelationshipsbetweenthesetasks,promotinginterconnectivitywithinthe
roadnetwork.
To improve the connectivity of road surfaces, additional information about roads,
such as road nodes and intersections, is also extracted by many scholars in multi-task
extraction. D.Chenetal.[129],whileusingnetworkmodelstoextractroadsurfaces,also
extractinformationaboutroadnodes. Thisnodeinformationprovidessupervisionforroad
surfaces,contributingtotheircontinuousimprovementinconnectivity. X.Chenetal.[130]
constructedanodeinferencebranchwithinthenetwork,modelingroadnodestogether
with road surfaces, thereby enhancing the topological structure of roads and reducing
surface fragmentation. Roads and intersections are two crucial elements in road net-
workgeneration. Lietal.[102]usingtrajectorydataandremotesensingimages,andnot
onlyextractedroadsurfacesbutalsorecoveredintersectioninformationfromroadarea
features,simultaneouslyperformingroadsurfaceandintersectionextractiontasks. Addi-
tionally,someresearchersapplymulti-taskingtosegmentationandchangedetection. M.
Zhouetal.[100]proposedaneuralnetworkwithdual-taskroadchangedetection,called
dual-taskdominantTransformer-basedneuralnetwork(DT-RoadCDNet). Thisnetwork
takesinputfromtwo-phaseremotesensingimagesandcanperformbothsegmentation
andchangeidentificationtasks,resultingintworoadsurfacesegmentationimagesbefore
andafterchangesandoneroadchangeimage.

Sensors2024,24,1708 16of31
Roadsarenotonlycomposedofroadsurfacesbutalsoincludeelementssuchasroad
centerlines, road edges, and road nodes. The emergence of multi-task road extraction
hasthepotentialtoenhanceroadinformation,facilitatingbetterroadpipelineplanning.
However, in current road extraction tasks, research focused on road centerlines as the
primaryextractiontaskisrelativelyscarce,withmostrelyingonlabeleddataprovided
byOpenStreetMap(OSM).Roadcenterlinesarenotonlyvitalcomponentsofroadsbut
canalsoserveasweaklabelsforsubsequenttasksbasedonweaksupervisionlearning.
Additionally,roadedgesandroadnodesareequallycrucial. Edgesdeterminetheintegrity
and continuity of road surfaces, while linear elements consist of nodes. Nodes can be
usedasadditionalinformationforpredictingandinferringroadsurfacebreakpointsand
completing linear elements, thus improving road connectivity. They can also serve as
road backbones, facilitating subsequent road vectorization processing. Road networks
evolveandchangeeachyear,andelectronicmapsrequiretimelyupdatesofroadnetworks.
Traditional methods often require substantial human and material resources for field
surveys. Roadchangedetectiontasksrelyonneuralnetworksandremotesensingimages,
automating the extraction of road changes from images, reducing the need for manual
intervention. However,duetolimitationsindatasourcesandlabels,changedetectiontasks
stillfaceissuesofmisseddetectionsandfalsealarms,necessitatingfurtherimprovementin
datasourcequality,labelquality,andnetworkmodelquality.
2.6. RoadFeatureExtractionBasedonNetworkOptimization
Thevariousstrategiesemployedbyresearchscholarsinoptimizingthetrainingof
network models are research hotspots, and the primary focus is loss functions. Loss
functionsplayanindispensableroleinthetrainingofnetworkmodels,astheymeasure
thedifferencebetweenthemodel’spredictionsandthegroundtruth. Modelperformance
istypicallyevaluatedbycalculatingthelossvalue,wherelowerlosssignifiesbettermodel
performance,indicatingthatthemodel’spredictionsareclosertothegroundtruth.
We find that the dice coefficient loss, binary cross entropy loss, and cross entropy
lossarethemostcommonlyusedlossfunctions. Sinceroadextractiontasksaretypically
binarysemanticsegmentationtasks,binarycrossentropylossismorecommonthancross
entropyloss. Additionally,inmodeltraining,thedicecoefficientlossisusedtomeasure
the similarity between predicted results and labels, while binary cross entropy loss is
employedtoassessthedistancebetweenpredictedresultsandactuallabels. Forinstance,
Lin et al. [72] introduced both of these loss functions into their proposed SE-DeepLab
networkandcomparedtheireffectivenessinmodeltraining. Theyfoundthatthediceloss
wasbettersuitedfortheirmodel,significantlyenhancingitsperformanceduringtraining
andprediction. Similarly,Lanetal.[53]alsoarguedthatthedicecoefficientlossismore
suitableforroadsegmentationtasksbecauseitconductsglobalassessment,whereasbinary
crossentropylossispixel-wise. Whenextremeimbalanceexistsbetweenforegroundand
background,binarycrossentropylossmaynoteffectivelyaddressthisissue. However,the
dicecoefficientlossissensitivetonoiseandmayoverlookboundaryinformation,leading
topoorerroadedgesegmentation. Toaddressthisconcern,ZaoandShi[131]proposedan
edge-focusedloss,whichguidesthenetworktopaymoreattentiontoroadedgeregions.
Additionally,theyintroducedanenhancementfactorthatassignshigherlosscontributions
topixelsclosertotheedges,therebyimprovingroadboundarysegmentation.
Different types of loss functions are combined, which is a training strategy used
bytheD-LinkNet. Thelossfunctionswereintegratedbyusingvariouscombinationsof
strategies[58,79,132]tofullyexploittheirrespectiveadvantagesinroadextraction. For
example,Abdollahietal.[133]introducedtheVNetnetworkmodelforroadextraction
andproposedanewdual-lossfunctioncalledcrossentropyanddiceloss(CEDL).Thisloss
functioncombinescrossentropy(CE)anddiceloss(DL)becausecrossentropyconsiders
localinformationwhiledicelossfocusesmoreonglobalinformation.IntroducingtheCEDL
lossfunctionintoVNetcanreducetheimpactofclassimbalanceissues,thusimproving
road extraction results. Since high-resolution remote sensing images typically include

Sensors2024,24,1708 17of31
complexbackgroundssuchasocclusion,shadows,andsimilartexturesinthesurrounding
terrain,manyroadsaredifficulttoidentifysuccessfully,leadingtoarelativelyhighrateof
omissions. Toaddressthischallenge,Luetal.[128]introducedthehardexamplemining
(HEM)lossfunction. Thislossfunction,byjointlyusingdiceandbinarycrossentropyloss
functions,paysmoreattentiontohardsamples,enhancingroadrecognitionandfurther
improvingroadcompleteness.
Toaddresstheissueofsampleimbalance,thefocallossfunctionhasbeenemployed
by some researchers [28,89,134]. Additionally Wei and Zhang [57] combined focal loss
withthedicefunction. Thefocallossfunction[135]differsfromtraditionalcrossentropy
functionsbyfocusingonresolvingsampleimbalancesandconfoundingpixelcategories.
Abdollahietal.[136]introducedalossfunctioncalledmedianfrequencybalancingfocal
lossweighted(MFB_FL)basedonthefocallossfunctiontodealwithhighlyimbalanced
datasets,wherepositivesamplesarescarce. TheintroductionofMFB_FLeasestheburden
on simple samples, allowing more time to be spent learning difficult samples, thereby
improvingroadextractionandroadvectorizationresults.Theissuehasalsobeenaddressed
bysomeresearchersthroughmodificationstothelossfunction.YangandWang[109]added
aspatialpenaltytermtothelossfunctiontoaddressthetypicalclassimbalanceissueinroad
extraction. Additionally,thesoftmaxcrossentropyloss(SCE),Jaccard,andLovaszsoftmax
(LZS)lossfunctionshavebeenappliedinbinaryroadextractiontasks. J.Zhangetal.[61]
combinedJaccardandcrossentropylossesinthetrainingoftheSDG-LinkNetmodelto
avoidtheproblemofsinglecrossentropyeasilyfallingintolocaloptima. Furthermore,
Sushmaetal.[137]simultaneouslyusedLZSandboundarylossfunctionsduringmodel
training,withresultsshowingtheirsuperiorityoverthemeansquarederror(MSE)loss.
Withrelativelylimitedresearchonlossfunctionsinroadextractiontasks,anattention
lossfunctioncalledGapLosswasproposedbyYuanandXu[138]. Thisfunctioncanbe
combinedwithanysegmentationnetwork. Firstly,abinarypredictionmaskisobtained
usingadeeplearningnetwork. Secondly,avectorskeletonisextractedfromtheprediction
mask. Thirdly, for each pixel, eight adjacent pixels with the same value are calculated,
andifthevalueis1,thepixelisidentifiedasanendpoint. Fourthly,basedonthenumber
of endpoints within a buffer range, the corresponding weight is assigned to each pixel
in the predicted image. Finally, the weighted average of the cross entropy of all pixels
in the batch is used as the final loss function value. GapLoss was introduced into four
relativelybasicnetworkmodels(PSPNet,U-Net++,SegNet,andMUNet),andthetraining
resultsoutperformedtheuseofthethreelossfunctions: dice,binarycrossentropy,and
focal. ThissuggeststhatGapLossnotonlyimprovestheconnectivityofpredictedroads
butalsoenhancestheaccuracyofroadpredictions. Xuetal.[139],basedontheD-LinkNet,
comparedtwelvewell-knownlossfunctions,categorizingthemintoregion-based(suchas
dice,Jaccard,andfocal),distribution-based(suchasbinarycrossentropy),andcomposite-
based(suchasacombinationofdiceandbinarycrossentropy). Theyfoundthatdifferent
lossfunctionsperformedsignificantlydifferentlyunderdifferentmodels. Region-based
lossfunctionsgenerallyoutperformeddistribution-basedones,whiletheperformancesof
region-basedandcomposite-basedlossfunctionswerecomparable. Thisindicatesthatthe
choiceofthemostsuitablelossfunctionshouldbebasedonthemodel’sdesign.
Inadditiontotheutilizationoflossfunctionsforoptimizingmodeltraining,thetradi-
tionalbatchnormalization(BN)layerhasbeenreplacedwithfilterresponsenormalization
(FRN)intheupsamplinglayerbysomeresearchers[27,140]. Withtheintroductionofthis
layer,themodeldecreasesitsdependenceonrandombatches,therebybenefitingmodel
optimizationandenhancingtrainingefficiency.
Thissectionprimarilyintroducesthefundamentalsofnetworkoptimizationinroad
extractiontasks,withanemphasisontheutilizationoflossfunctions.Additionally,itbriefly
mentionsadjustmentsmadebetweendifferentlayersofthemodeltoenhancethemodel’s
trainingcapabilities. Concerningtheapplicationoflossfunctions,binarycrossentropy,
diceloss,andtheircombinationsrepresentthemostcommonlyemployedlossfunctionsin
modeltraining. However,duetovariationsinherentindifferentmodels,theperformance

Sensors2024,24,1708 18of31
of various loss functions may exhibit differences. Furthermore, it is worth noting that
thereisrelativelylimitedin-depthresearchonlossfunctionsintheroadextractionfield.
Althoughdicelossandbinarycross-entropy–dicecombinationsarepresentlyregardedas
moresuitablelossfunctions,thequestionofwhethertheselossfunctionscanconsistently
perform well in new models that are deeper, wider, and larger warrants consideration.
Therefore,oneofthefutureresearchdirectionsinvolvesthedesignoflossfunctionswith
stronggeneralizationcapabilitiesaimedatimprovingperformanceondiversemodels.
3. RoadFeatureExtractionBasedonSemi-Supervised(Weak)DeepLearning
NetworkModels
Semi-supervised learning falls within the domain of weakly supervised learning,
combiningelementsofbothunsupervisedandsupervisedlearning. Itconsistsofasuper-
vised learning part and an unsupervised learning part. Zhou [141] subdivided weakly
supervisedlearningintothreecategories: (1)incompletesupervisionreferstothesituation
whereonlyaportionofthetrainingdataarelabeled,andtherestareunlabeled. (2)Inexact
supervisionreferstotheprovisionofcoarse-grainedlabelinformationinthetrainingdata,
whichismorecommonintaskssuchasobjectdetectionandinstancesegmentationbut
lessprevalentinroadextractiontasks,whereroadextractionistypicallyabinarysemantic
segmentationproblem. (3)Inaccuratesupervisionmeansthatthelabelsinthetrainingdata
maycontainerrorsorinaccuracies,whichareinevitableinroaddatasetsbecauseroadla-
belingtypicallyinvolvesmanualannotation. Theauthorproposescorrespondingsolutions
forthesethreetypesofsupervision. Forincompletesupervisionproblems,activelearning
orsemi-supervisedlearningmethodsareused. Additionally,multi-instancelearningcan
beappliedtoaddressinexactsupervisionproblems. Forinaccuratesupervisionproblems,
learningwithlabelnoisestrategiesisemployed,introducingnoisetothelabelsformodel
training. Insummary,bothsemi-supervisedlearningandweaklysupervisedlearningrely
onasmallamountoflabeleddataandalargeamountofunlabeleddatafortrainingmodels
andimprovingperformance. Inthefieldofroadextraction,researchershaveusedvarious
methodstoaddresstheissueoflimitedlabeleddata. Thissectionwillexplorethisissue
fromtheperspectivesofweaklysupervisedlearningandsemi-supervisedlearning.
3.1. RoadFeatureExtractionBasedonWeaklySupervisedLearning
In weakly supervised road extraction tasks, the challenge of acquiring pixel-level
labeled data at a high cost and difficulty is encountered by researchers. Therefore, the
exploration of alternatives such as weak label data, such as point or line annotations,
hasbecomeafocus. Thesedataarecomparativelyeasiertoobtainandmoreabundant
thanpixel-levellabels,makingthemthepreferredchoiceforresearchers. Forinstance,a
methodknownas“deepwindows”[142]effectivelyutilizespointannotationdatainroad
centerlineextractiontasks. Ablock-basedroadcenterpointestimationmodelwasinitially
designed,inspiredbythestackedhourglassnetworksappliedinthefieldofhumanpose
estimation [143]. This model was then trained using point annotations (indicating the
centerpointsofroadsintrainingblocks)topredictroadcenterpointswithinlocalblocks.
Subsequently,thedirectionoftheroadwasestimatedusingtheFourierspectrumanalysis
algorithm. GuidedbytheCNNmodel,roadcenterpointswithinblockswereiteratively
trackedandconnectedalongtheroad’sdirection,completingtheroadcenterlineextraction.
Buildinguponthismethod,LianandHuang[144]furtherdevelopedapoint-basedweakly
supervisedroadsegmentationmethodforroadsurfaceextraction. Pointannotationdata
wereinitiallyutilizedtodetectroadseedpointsandbackgroundpointsinremotesensing
images. Thesepointswerethenusedtotrainasupportvectormachineclassifier(SVC)
forclassifyingeachpixelintheimageasroadornon-road. Simultaneously,amulti-scale
andmulti-directionGaborfilterwasintroducedtoestimatetheroadpotentialofeachpixel
basedonthepreliminaryclassificationresults,takingintoconsiderationthelocalgeometric
anddirectionalfeaturesoftheroad. Finally,anactivecontourmodelalgorithmbasedon

Sensors2024,24,1708 19of31
localbinaryfittingenergy(LBF-Snake)wasintroducedtoextractroadcontoursfromnon-
uniformroadpotentialmapsandoptimizeroadregionsthroughsimplepost-processing.
Theweaklysupervisedroadsurfaceextractionmethod“ScRoadExtractor”waspro-
posed[145]. Thismethodutilizesroadcenterlinesaslinedrawinglabeldataandcombines
remotesensingimageswitharoadlabelpropagationalgorithmtogeneratepseudo-labels.
Holisticallynestededgedetection(HED)wasemployedforedgedetectionwithintheim-
ageryboundary. Additionally,anetworkmodelwithadual-semanticbranch(DBNet)was
designedfortraining. Themodel’sprimarybranchisbasedonanencoder–decoderstruc-
ture,withResNet-34servingastheencoderbackbone. Theintermediatelayerincorporates
atrousspatialpyramidpooling(ASPP).Thedecoderincludesroadsurfacesegmentation
and road boundary detection branches, which utilize segmentation and boundary loss
functionstoassessthesimilaritybetweenthesegmentationresultsandpseudo-labelsand
theedgesegmentationresultsandedgedetection. Thisenablesthenetworktoiteratively
optimizeandimproveroadextraction. M.Zhouetal.[146]observedthatinthepresenceof
backgroundocclusionandspectralconfusioninremotesensingimages,roadedgestend
toappearblurry. Usingsingle-pixel-widthlinedrawinglabelsalonetoapproximatethe
positionofroadcenterlinesdoesnotoffersufficientsupervisionforroadboundarylearn-
ing. Consequently,thisresultsindecreasedaccuracyinroadsurfacesegmentationwhen
employinglinedrawingsupervisionmethods. Theyalsoconsideredthelabelpropagation
algorithmtobeoverlycomplexand,asaresult,optednottouseit.Instead,theyintroduced
aweaklysupervisedroadsegmentationnetwork,SOC-RoadNet,basedonstructuraland
directionalconsistency. SOC-RoadNetutilizeslinedrawinglabelsasweaksupervisionfor
roadsurfaceextractionfromremotesensingimages. SOC-RoadNetfeaturesadual-branch
architecture,encompassingaroadsegmentationbranchandaroaddirectionprediction
branch. Theroadsegmentationbranchdirectlylearnsroadsurfacefeaturesfromtheline
drawinglabels,whilethedirectionpredictionbranchpredictscontinuousroaddirections
toenhanceroadconnectivity. Ratherthanregularizingroadboundariesusingunreliable
edge maps, SOC-RoadNet improves the accuracy of road boundaries by introducing a
structuralconsistencylossfunction. Thesemethodsillustratehowtojudiciouslyleverage
pointandlineannotationstoenhanceroadextractionperformanceandaccuracywithina
weaklysupervisedlearningframework.
3.2. RoadFeatureExtractionBasedonSemi-SupervisedLearning
Whenapplyingsemi-supervisedlearningtoroadextractiontasks,threemainaspects
aretypicallyaddressed. Thefirstinvolvesconsistencyregularization,oftenentailingtwo
branches, each dealing with samples subject to different perturbations. Through loss
functions,thepredictionsofthesetwobranchesareencouragedtoremainconsistent. This
meansthatsomeformofperturbation(e.g.,flipping,rotating,cropping,andmirroring)
isappliedtounlabeledsampledata,andthemodel’spredictionsshouldexhibitminimal
changes. Thesecondaspectpertainstoadversarialtraining,whereinadversarialstrategies
areappliedtounlabeleddatatoaligntheoutputsofunlabeleddataascloselyaspossible
withthedistributionofrealdata. Finally,pseudo-labelingisthethirdaspect,involving
aninitialmodeltrainingusinglabeleddata. Subsequently,thetrainedmodelisutilized
to make predictions for unlabeled data, high-confidence samples (above a pre-defined
threshold)areselected,andtheirpredictedresultsareusedaspseudo-labels. Thesepseudo-
labeled data are integrated into the labeled dataset, and the model undergoes further
trainingonthisexpandedlabeleddatasetthroughaniterativeprocessaimedatongoing
modeloptimization. Ingeneral,thesemethodsareaimedataddressingchallengessuchas
limitedlabelavailabilityandhighannotationcosts.
(1) Basedontheconsistencyregularization
Whenapplyingsemi-supervisedlearningtoroadextractiontasks,thethreeapproaches
mentioned above have been utilized by researchers. For instance, the introduction of
theideaofconsistencyregularizationintoroadextractionwaspresented[147]. Asemi-
supervisedsemanticsegmentationmethodforfine-grainedroadsceneunderstandingwas

Sensors2024,24,1708 20of31
designed. Fourperturbationstrategieswereemployed,encompassingrandomgrayscale,
randomblur,randomcolorjitter(brightness,contrast,saturation,etc.),andrandomGaus-
siannoise. Adual-branchstructurewasimplemented,withonebranchperturbingunla-
beleddataandtheotherbranchpreservingtheoriginalimage. Thecombinationoflabeled
and unlabeled samples in a U-Net model, with a balanced strategy of supervised and
unsupervisedlosses,enabledtheefficientextractionofroadsceneinformation,including
vehicles, roadlines, crosswalks, groundmarkings, andlanewidths. Thisapproachnot
only improved the classification accuracy of semantic segmentation networks but also
mitigatedthenegativeimpactoflimitedlabeleddataonnetworkperformance. Inanother
study [148], which focused on consistency regularization in semi-supervised learning,
perturbation schemes were reviewed, and prominent data-level perturbation schemes,
CutMixandClassMix(adevelopmentfromCutMix),aswellasmodel-levelperturbation
representatives,meanteacher(MT)andcrosspseudo-supervision(CPS),wereidentified.
Inspired by these four perturbation methods, an end-to-end semi-supervised semantic
segmentationframeworknamed“ClassHyPer”wasproposed. Thisframeworkisbased
ontheClassMixstructureandsimultaneouslyincorporatesMTandCPSperturbationsto
formamixedperturbationstrategy. Theimagessubjectedtothesemixedperturbations
were then processed through a classic FCN with VGG16 as the backbone structure. By
employingvariouslossfunctionstocalculatesamplecorrelations,ClassHyperexhibited
strongperformanceonfivedifferenturbanandroaddatasets,demonstratingitspotential
inenhancingmodelperformancewhenconfrontedwithlimitedlabeleddata.
(2) Basedontheconsistencyregularizationandpseudo-labels
Theconceptofconsistencyregularizationandpseudo-labelingwasintroducedinto
semi-supervised road extraction tasks by You et al. [149], who proposed a novel semi-
supervised remote sensing road extraction method called “FMWDCT”. This method
comprisestwokeycomponents:dual-networkcrosstraining(DCT)andforegroundpasting
(FP). The objective of dual-network cross training is to address common challenges in
remotesensingimagesegmentationtasks,suchaslimitedtrainingdataandhighannotation
costs.Foregroundpastinginvolvestheintegrationofforegroundpixelsfromlabeledimages
intounlabeledimages,generatingmixedinputimages. Thisstrategyaimstotacklethe
issueofimbalancedpositiveandnegativetrainingsamplesinroadextractiontasks. In
FMWDCT,eachnetworkincludesbothaninitialnetworkandanenhancementnetwork.
Mixedpseudo-labelsaregeneratedbycombininghigh-confidencepredictionsfromthe
enhancementnetworkandlabeledmasks. Subsequently,thesemixedpseudo-labelsare
employed to guide cross training in another adversarial base network and to facilitate
smoothingupdatesinthecorrespondingenhancementnetwork. Thisapproachcontributes
totheenhancementofroadextractioninsituationsinvolvinglimitedlabeleddatawhile
harnessingthepotentialofunlabeleddataandpseudo-labeling.
(3) Basedonadversarialtrainingandpseudo-labels
Thesemi-supervisedroadextractionproblemwasaddressed[150]throughtheuti-
lizationofadversarialtrainingandpseudo-labeling. Theyintroducedaninnovativesemi-
supervisedroadextractionnetworkknownas“SemiRoadExNet”,whichisdesignedbased
ongenerativeadversarialnetworks(GANs)andcomprisesageneratorandtwodiscrim-
inators. Thegeneratorfollowsanencoder–decoderstructure,utilizingResNet-34asthe
encoderbackbone,andintroduceschannelattentionandspatialattentioninaserialstrategy.
Additionally,multipledilatedconvolutionswithskipconnectionsareincorporatedinthe
middle layers. Two discriminators, based on the U-Net architecture, are employed for
differenttasks. TheworkingprincipleofSemiRoadExNetisasfollows: first,labeledand
unlabeledimagesareinputintothegeneratornetworkforroadextraction. Thegenerator’s
outputincludesroadsegmentationresultsandtheircorrespondingentropymaps. The
entropymaprepresentstheconfidencelevelforeachpixel’spredictionofroadornon-road.
Next,twodiscriminatorsareutilizedtoenforcetheconsistencyoffeaturedistributionsbe-
tweentheroadpredictionmapsandentropymapsoflabeledandunlabeleddata. Through

Sensors2024,24,1708 21of31
adversarialtraining,thegeneratoriscontinuouslyregularized,exploringlatentinforma-
tion within unlabeled data and enhancing the model’s generalization capability. This
methodaimstomaximizetheutilizationofpotentialinformationinlow-confidencepixels
in pseudo-labels, further enhancing semi-supervised road extraction models, reducing
relianceonlabeleddata,andimprovingnetworkperformance.
3.3. RoadFeatureExtractionBasedonSemi-WeaklySupervisedLearning
Anovelapproach[151]combinesthestrengthsofsemi-supervisedandweaklysu-
pervisedlearning,resultinginamethodknownassemi-weaklysupervisedlearning. In
this context, adversarial training from semi-supervised learning and the utilization of
weaklabels(suchasroadcenterlines)fromweaklysupervisedlearningwereleveragedto
proposearemotesensingimageroadextractionmodelnamed“SW-GAN”. SW-GANcom-
prisestwogeneratorsandonediscriminator. Thesegeneratorsincludeafullysupervised
generatorbasedontheD-LinkNetmodelandaweaklysupervisedgeneratorbasedonthe
Res-UNetmodel,whichincorporateslearnablepyramiddilatedmodulesintothemiddle
and skip connection layers to expand the receptive field. The training dataset includes
bothfullysupervisedandweaklysuperviseddatasets. Duringthetrainingprocess,the
fullysupervisedgeneratorusesboththefullysupervisedandweaklysuperviseddatasets,
whiletheweaklysupervisedgeneratorutilizesonlytheweaklysuperviseddataset. The
outputoftheweaklysupervisedgeneratorisemployedasafeaturetoaugmentthefully
supervised generator. To ensure consistency between the fully supervised and weakly
supervised generators on the weakly supervised dataset, a consistency loss function is
designedtoencouragebothgeneratorstoproduceresultsthatareassimilaraspossible.The
discriminatoremploysanFCNmodel,aimingtodistinguishwhetherthegeneratedroad
networkisapixel-levelmanuallyannotatedroadnetworkorfullysupervisedsynthesized
roadnetwork. SW-GANeffectivelyutilizesalimitedamountoffullysuperviseddataand
a substantial amount of weakly supervised data for road network extraction in remote
sensing images, combining the advantages of semi-supervised and weakly supervised
learningandachievingoutstandingroadextractionresults.
4. Discussions
Thispaperstartsfromtheperspectiveofsupervisedlearningindeeplearning,em-
phasizingthetechnicalintricaciesinvolvedinroadextractionfromremotesensingimages,
andcategorizessupervisedlearningintofourmethodsbasedontheuseofpixel-levellabel
data. TheadvantagesanddisadvantagesofthefourlearningmethodsarelistedinTable4.
Foramorecomprehensiveevaluationofmodelperformances,weprimarilyassessthe
accuracyofthemodelsbasedonfivekeymetrics,namelyintersectionoverunion(IoU),
overallaccuracy(OA),Precision,Recall,andF1. IoUindicatestheoverlapbetweenthe
predictedandgroundtruthroadareasinroadextractiontasks. OAdenotestheaccuracy,
signifyingtheratioofcorrectlypredictedpixelstothetotalpixels. Precisionreflectsthe
proportionofaccuratelypredictedroadpixelsbythemodel,whileRecallmeasuresthe
numberofroadsidentifiedbythemodel. F1istheharmonicmeanofPrecisionandRecall.
Simultaneously,wehaveoutlinedtheperformanceofseveralmodelsontheroaddataset
ofMassachusetts,asdepictedinTable5.
LDANet[97]demonstratesexceptionalperformanceintermsofRecall,Precision,and
F1-Score,showcasingitsabilitytoaccuratelyidentifyroadpixelswhileeffectivelyreducing
false positives. Furthermore, LDANet boasts an impressively low parameter count of
only0.2M,positioningitselfasanoutstandinglightweightmodel,therebyhighlightinga
promisingdirectionforfutureresearchandadoption. Seg-Road-I,DU-Net,CM-FCN,and
othersexhibitcommendableperformanceacrossmultiplemetrics,showcasingelevated
levelsofRecall,Precision,andF1-Score. SimilartoLDANet,theyserveasrepresentatives
ofhigh-performancemodelsinthisdomain.

Sensors2024,24,1708
22of31
Table4.Comparisonof4learningmethods.
|     |              | LabeledData |     | Extraction |     | Generalization |     |     | Prospectsfor   |               |     |
| --- | ------------ | ----------- | --- | ---------- | --- | -------------- | --- | --- | -------------- | ------------- | --- |
|     | LearningType |             |     |            |     |                |     |     |                | Disadvantages |     |
|     |              | Usage       |     | Accuracy   |     | Ability        |     |     | FutureResearch |               |     |
Requiressubstantial
humaneffortandcostto
|                 |          | Largeamountof |     |              |     |                |     | Excellentresultswith   |     |                        |     |
| --------------- | -------- | ------------- | --- | ------------ | --- | -------------- | --- | ---------------------- | --- | ---------------------- | --- |
| FullySupervised |          |               |     |              |     |                |     |                        |     | labeldata.Itmayoverfit |     |
|                 |          | high-quality  |     | Highaccuracy |     | Relativelypoor |     | sufficientlabeleddata, |     |                        |     |
|                 | Learning |               |     |              |     |                |     |                        |     | tolabeleddataandlack   |     |
|                 |          | labeleddata   |     |              |     |                |     | limitedgeneralization  |     |                        |     |
adaptabilitytounseen
scenarios
Complexityindesigning
algorithmsthat
Potential
|     |     | Smallamountof |     |     |     |     |     |     |     | effectivelyleverageboth |     |
| --- | --- | ------------- | --- | --- | --- | --- | --- | --- | --- | ----------------------- | --- |
Semi-Supervised Lowerthanfully Betterthanfully improvementsthrough
|     |          | labeleddata+  |     |            |     |            |     |                      |     | labeledandunlabeled |     |
| --- | -------- | ------------- | --- | ---------- | --- | ---------- | --- | -------------------- | --- | ------------------- | --- |
|     | Learning |               |     | supervised |     | supervised |     | utilizingbothlabeled |     |                     |     |
|     |          | unlabeleddata |     |            |     |            |     |                      |     | data,riskoferror    |     |
andunlabeleddata
propagationfrom
weaklabels
Difficultyinensuring
|     |     |     |     |     |     |     |     | Promisingduetoease |     | accuracyduetothenoise |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------------ | --- | --------------------- | --- |
WeaklySupervised Largeamountof Lowerthanfully ofobtainingweak orambiguitypresentin
|     |          | weaklylabeled |     |            |     | Stronggeneralization |     |                 |     |                      |     |
| --- | -------- | ------------- | --- | ---------- | --- | -------------------- | --- | --------------- | --- | -------------------- | --- |
|     | Learning |               |     | supervised |     |                      |     | labelsandbetter |     | weaklabels,potential |     |
data
|     |     |     |     |     |     |     |     | generalization |     | inconsistencyin |     |
| --- | --- | --- | --- | --- | --- | --- | --- | -------------- | --- | --------------- | --- |
labelingquality
Balancingaccuracyfrom
|     |     | Combinationof |     |     |     |     |     |     |     | labeleddatawith |     |
| --- | --- | ------------- | --- | --- | --- | --- | --- | --- | --- | --------------- | --- |
Opportunitytoharness
|     | Semi-Weakly | smallamountof |     |     |     |     |     |     |     | generalizationfromweak |     |
| --- | ----------- | ------------- | --- | --- | --- | --- | --- | --- | --- | ---------------------- | --- |
thebenefitsofboth
Supervised labeleddata+large Moderateaccuracy Stronggeneralization labels,potential
labeledandweakly
|     | Learning | amountofweakly |     |     |     |     |     |             |     | challengesin            |     |
| --- | -------- | -------------- | --- | --- | --- | --- | --- | ----------- | --- | ----------------------- | --- |
|     |          | labeleddata    |     |     |     |     |     | labeleddata |     | harmonizingthedifferent |     |
typesoflabeleddata
Table5.ThePerformanceComparisonofModelsontheMassachusettsDataset.
|                        | Method             |     | Recall | Precision | F1-Score |     | OA    |     | IoU   | mIoU  | Parameters(M) |
| ---------------------- | ------------------ | --- | ------ | --------- | -------- | --- | ----- | --- | ----- | ----- | ------------- |
|                        | SegRExt-A[67]      |     | 68.29  | 76.95     |          | -   | 97.53 |     | 56.82 | -     | -             |
|                        | SegRExt-F[67]      |     | 63.84  | 74.88     |          | -   | 96.62 |     | 52.85 | -     | -             |
|                        | MSPFE-Net[57]      |     | 75.50  | 73.11     | 74.29    |     | -     |     | 59.09 | -     | -             |
|                        | LDANet[97]         |     | 97.07  | 97.55     | 97.31    |     | -     |     | 68.34 | -     | 0.20          |
|                        | SemiRoadExNet[150] |     | -      | -         | 70.23    |     | -     |     | 54.66 | -     | -             |
|                        | Seg-Road-I[70]     |     | 92.86  | 87.34     | 90.02    |     | -     |     | 68.38 | 83.89 | 28.67         |
|                        | DU-Net[74]         |     | 96.96  | 97.48     | 96.72    |     | -     |     | -     | 67.05 | -             |
|                        | SR[31]             |     | 77.50  | 80.41     | 78.93    |     | -     |     | -     | 65.30 | -             |
|                        | MECA-Net[66]       |     | 78.19  | 80.63     | 79.39    |     | -     |     | 65.82 | -     | -             |
|                        | GA-Net[130]        |     | 76.89  | 84.10     | 80.33    |     | -     |     | 67.13 | -     |               |
|                        | SDG-DenseNet[61]   |     | 77.67  | 81.86     | 79.63    |     | -     |     | 66.47 | -     | 265.00        |
|                        | SDUNet[96]         |     | 75.70  | 81.20     | 78.40    |     | -     |     | 74.10 | -     | 80.24         |
|                        | MUNet[138]         |     | -      | -         | 67.40    |     | 97.20 |     | -     | 74.00 | -             |
| U-Net+++Resnext[152]   |                    |     | 95.10  | 94.30     | 94.70    |     | -     |     |       | -     |               |
| DeepresidualU-Net[153] |                    |     | 80.00  | 84.00     | 81.00    |     | -     |     | 72.00 | -     | -             |
|                        | CM-FCN[82]         |     | 77.87  | 79.45     | 78.65    |     | 97.98 |     | 67.55 | -     | 56.45         |
|                        | CRAE-Net[83]       |     | 79.35  | 80.04     | 79.52    |     | -     |     | 66.27 | -     | 49.18         |
|                        | SGCN[154]          |     | 73.91  | 84.82     | 78.99    |     | -     |     | 81.65 | 65.28 | 42.73         |
|                        | RicherU-Net[131]   |     | -      | -         |          | -   | -     |     | 58.63 | -     | -             |
|                        | GDCNet[122]        |     | 71.21  | 84.43     |          | -   | -     |     | 62.94 | -     | -             |
|                        | ConSwin[69]        |     | 79.17  | 81.11     | 80.13    |     | 98.15 |     | 66.84 | -     | -             |
|                        | RALC-Net[1]        |     | -      | -         | 74.70    |     | -     |     |       | 59.61 |               |
|                        | RoadVecNet[136]    |     | -      | -         | 92.51    |     | -     |     | 86.31 | -     | -             |

Sensors2024,24,1708
23of31
Table5.Cont.
| Method               | Recall | Precision | F1-Score | OA    | IoU   | mIoU Parameters(M) |      |
| -------------------- | ------ | --------- | -------- | ----- | ----- | ------------------ | ---- |
| MCG-UNet[119]        | 86.59  | 91.18     | 88.74    | -     | 79.92 | -                  |      |
| AEMLU-Nets[125]      | 76.33  | 81.06     | 78.62    | -     | 64.77 | -                  | -    |
| RVgg19[155]          | 91.02  | 84.98     | 87.90    | -     | -     | -                  | -    |
| CADUNet[78]          | 76.55  | 79.45     | 77.89    | 98.00 | 64.12 | -                  | -    |
| AF-Net[94]           | -      | -         | -        | -     | 67.25 | -                  | -    |
| E-UNet[118]          | 81.30  | 80.71     | 80.45    | 97.59 | 68.56 | -                  | -    |
| DCANet[93]           | 79.54  | 80.20     | 79.84    | 98.09 | 66.45 | 82.23              | 11.1 |
| DeepFRTransNet[91]   | 78.13  | 83.72     | -        | 97.48 |       | 62.86              | -    |
| Prop-GAN[7]          | 92.92  | 91.54     | 92.20    | -     |       | 87.43              | -    |
| DGRN[56]             | 71.97  | -         | 76.59    | -     | 62.48 | -                  | -    |
| CNN-Based[126]       | 85.88  | 78.47     | -        | -     | 78.65 | -                  | -    |
| NestedSE-Deeplab[72] | -      | 85.80     | 85.70    | 96.70 | 73.87 | -                  | -    |
| DiResNet[124]        | 79.41  | 80.38     | 79.70    | 98.13 | -     | -                  | -    |
| CDG[77]              | 71.80  | 81.41     | 76.10    | -     | 61.90 | -                  | -    |
| VNet+CEDL[133]       | -      | -         | 91.18    | -     | 83.82 | -                  | -    |
ConSwin, DCANet, and DiResNet all have overall accuracy (OA) exceeding 98%.
ThishighOAindicatesthatthesemodelsexhibitaveryhighlevelofaccuracyincorrectly
classifyingroadandnon-roadpixelswithinthedatasettheywereevaluatedon.
Prop-GAN,DCANet, andSeg-Road-IexhibithighmIoU,withProp-GANachieving
thehighestmIoUamongthesemodels.Thissignifiestheirrobustnessandprecisioninroad
extractiontasks,indicatingtheircapabilitytoaccuratelyidentifyandextractroadinformation.
In conclusion, we have provided a more detailed summary of the limitations and
challengesassociatedwithcurrentmodelsinthecontextofroadextraction. Thefollowing
pointsencapsulateourfindings:
|     | (1) ModelComplexityvs. |     | InferenceSpeed |     |     |     |     |
| --- | ---------------------- | --- | -------------- | --- | --- | --- | --- |
Complexmodelsgenerallyconfersuperioraccuracy,however,atthepotentialexpense
of increased computational overhead and a higher number of parameters during the
inference phase. Looking forward, achieving a nuanced equilibrium between model
complexity and predictive speed is imperative, particularly in the context of real-time
applicationsforroadextraction.
|     | (2) Generalizationvs. |     | Specialization |     |     |     |     |
| --- | --------------------- | --- | -------------- | --- | --- | --- | --- |
Whenconfrontedwithunfamiliarroaddata, modelsdemonstratingexcessivespe-
cializationmayencounterchallenges,whilethosecharacterizedbyanoverlygeneralized
naturemayfailtocomprehensivelycapturethenuancedcomplexitieswithinspecificroad
domains. Achieving a judicious balance is crucial for optimizing performance across
diverseroadscenarios.
|     | (3) Interpretabilityvs. |     | ModelPerformance |     |     |     |     |
| --- | ----------------------- | --- | ---------------- | --- | --- | --- | --- |
Simplifiedmodelsareoftenprizedfortheirinterpretability,yettheymayfallshort
ofmatchingtheperformanceoftheirmoreintricatecounterparts. Whileroadextraction
maysuperficiallyappearasastraightforwardbinaryclassificationtask,certaindeepneural
networks—especially sophisticated architectures like the Transformer—are frequently
characterizedas“black-box”models. Thischaracterizationposeschallengesindeciphering
theirdecisionmakingprocessesandassessingtheirsuitabilityfordeploymentinbinary
classificationtasks. Furthermore,weunderscorethenotionthatemployingoverlycomplex
modelsforostensiblysimpletasksmightbeconstruedasaninstanceof“overengineering”.
Therefore,meticulousconsiderationiswarrantedintheselectionofmodels,navigatingthe
delicatebalancebetweeninterpretabilityandperformance.

Sensors2024,24,1708 24of31
5. Prospects
Despitesignificantprogressinthefieldofroadextractionfromremotesensingimages
inrecentyears,therearestillsomeissuesthatrequirefurtherresearchanddevelopment,
summarizedasfollows:
(1) ObtainingHigh-QualityLabeledSampleData
Thiscanbeaddressedbyemployingsemi-supervisedandweaklysupervisedlearning
methods,combininglimitedlabeledsampledatawithalargeamountofunlabeleddata.
Althoughthesemethodsmaynotachievethesamelevelofaccuracyinroadextractionas
fullsupervision,theyprovidenewapproachestoaddressingthischallenge. Furthermore,
we have observed that there is a relatively limited availability of open road datasets in
complexmountainousterrainswhenorganizingthedataset. Therefore,thereisaneedto
furtherexpanddataresourcesinthisregard.
(2) DifferencesinSpectralInformationDuetoFactorsSuchasSensorsandSolarAngles
Additionally,whendealingwithchallengeslikeroadocclusionandcomplexback-
groundinformation,relativelysimpleneuralnetworkscanbeemployedtoseparateroad
andnon-roadareasinadvance,therebyenhancingtherobustnessofthemodelinsubse-
quentrecognitiontasks. However,itisworthnotingthatresearchinareassuchasimage
denoisingandsuper-high-resolutionreconstructionremainsrelativelylimitedinthefield
ofdataenhancement.
(3) UtilizingMulti-ModalData
Currently,theapplicationofmulti-modaldatainroadextractionresearchisrelatively
limited. Multi-spectral (hyperspectral) data provide us with rich spectral information,
whileSARdatacompensateforthelimitationsofopticalimageswhendealingwithissues
like vegetation occlusion. However, LiDAR data are distinctive, typically in the form
of three-dimensional point cloud data, and there are significant differences in spatial
representation compared to two-dimensional road data. Therefore, further research is
neededintheareaofdatafusion. Scholarsinthisfieldhaveconductedrelativelylimited
research,leavingroomforfurtherexplorationinthefuture. Withthecontinuousexpansion
ofcrowdsourceddataandtheadvantagesofGNSSandothertrajectorydata,whichdonot
containadditionalenvironmentalinformationandhaveminimalinterference,theyhave
playedasignificantrolewhencombinedwithopticalimages. Thiscombinationprovides
uswithcomplementaryinformationandeffectivelymitigatesissuessuchasthelossof
roadintersectioninformationandincompleteconnections. Inthefuture,crowdsourced
datasetsfromplatformslikeGoogle,Amap,Didi,Baidu,andotherswillfurthersupport
andassistroadextraction.
(4) OptimizationofFullySupervisedLearningModels
Fromgenerativeadversarialnetworks(GANs)toconditionalgenerativeadversarial
networks(CGANs),andfromunsupervisedlearningtosupervisedlearning,theseadvance-
mentsallemphasizetheadvantagesofsupervisedlearninginroadfeatureextractionto
achievemoreidealroadextractionresults. Modelsbasedontheencoder–decoderstruc-
turearestillapopularresearchdirectioninthecurrentdeeplearningfield. Introducing
attentionmechanismmodulesindifferentstructures,achievingmulti-scalefeaturefusion,
consideringtheintroductionofTransformer,GCNs,anddeepconvolutionalseparation
structures,andevenintroducingcorrespondinglossfunctionsbasedonthemodel’scharac-
teristicsduringthetrainingprocessallcontributetoimprovingthemodel’sroadfeature
extractionperformanceinimages. Asmodelsmovetowardsgreaterdepthandwidth,an
increaseinmodelsizemayleadtoanexcessofparameters,therebyraisingtrainingcosts.
Therefore,seekinglighter,moreefficient,andmorehighlygeneralizablemodelsbecomes
animportantdirectionforfutureresearch.
(5) OptimizationofSemi-Supervised(Weak)LearningModels

Sensors2024,24,1708 25of31
Withtheemergenceofsemi-supervised(weak)learning,wehavesuccessfullyover-
comethechallengesofhighcostsandthedifficultyofobtaininglabelsbyusingasmall
amountoflabeleddataandalargeamountofweaklylabeledannotationdata. Wehave
employedvariousmethodsandstrategiesformodeltraining,achievingtrainingresults
approximatingthoseoffullysupervisedlearning.However,despitethesignificantprogress
madeinsemi-supervisedandweaklysupervisedlearning,thereisstillasubstantialgapin
accuracywhenitcomestoroadextractioncomparedtofullysupervisedlearning. Addi-
tionally,thereisrelativelylimitedresearchonmodelsbasedonsemi-weaklysupervised
learning. Therefore,futureresearchdirectionsshouldexplorehowtofullyintegratethe
respectivestrengthsofsemi-supervisedandweaklysupervisedlearningtocompensatefor
theirshortcomingsandbuildmorepowerfulsemi-weaklysupervisedmodels.
(6) RoadExtractionPost-Processing
Roadsegmentationisnottheendofroadextraction. Afterroadsegmentation,thereis
stillsignificantroomforthepost-processingofroadextraction. Thisisbecausethequality
of the model’s extraction cannot be solely measured by high or low accuracy. Further
observationisrequiredtoassesswhethertheconnectivityofroadsintheimageisintact
orifthereareissueslikefragmentation. Relevantpost-processingmethodscanbeused
torepairdamagedroadsandimprovetheconnectivityofpoorlyconnectedintersections.
Additionally, attention should be given to specific tasks such as vectorization of roads,
estimationofroadareas,andregistrationofroadfeatureswithaerialimagery. Thesetasks
areofgreatsignificancetofieldssuchasgeographicinformationsystems(GISs),urban
roadnetworks,andelectronicmapupdates. Conditionalgenerativeadversarialnetworks
(CGANs)canbeappliednotonlytoroadextractiontasksbutalsoprovidenewavenues
for road extraction post-processing. By utilizing the differences between the generator
and discriminator backbone models and additional conditions like adding noise and
artifacts,theyofferextensiveopportunitiesforthefuturedevelopmentofpost-processing
inthisfield.
AuthorContributions:Conceptualization,Y.S.;investigation,S.M.andQ.Y.;writing—originaldraft
preparation,S.M.;writing—reviewandediting,Y.S.andM.L.Allauthorshavereadandagreedto
thepublishedversionofthemanuscript.
Funding: ThisresearchwasfinanciallysupportedinpartbytheNaturalScienceFoundationof
JiangsuProvinceunderGrantBK20201387andQingLanProjectofJiangsuProvince(QL2021),China.
DataAvailabilityStatement:Datawillbemadeavailableonrequest.
Acknowledgments:Theauthorswouldliketothankthecontributionsoftheeditorandreviewers.
ConflictsofInterest:Theauthorsdeclarenoconflictsofinterest.
References
1. Liu,Z.;Wang,M.;Wang,F.;Ji,X.AResidualAttentionandLocalContext-AwareNetworkforRoadExtractionfromHigh-
ResolutionRemoteSensingImagery.RemoteSens.2021,13,4958.[CrossRef]
2. Li,P.;He,X.;Qiao,M.;Miao,D.;Cheng,X.;Song,D.;Chen,M.;Li,J.;Zhou,T.;Guo,X.;etal.ExploringMultipleCrowdsourced
DatatoLearnDeepConvolutionalNeuralNetworksforRoadExtraction. Int. J.Appl. EarthObs. Geoinf. 2021,104,102544.
[CrossRef]
3. Abdollahi,A.;Pradhan,B.;Shukla,N.;Chakraborty,S.;Alamri,A.DeepLearningApproachesAppliedtoRemoteSensing
DatasetsforRoadExtraction:AState-of-the-ArtReview.RemoteSens.2020,12,1444.[CrossRef]
4. Wei,Y.;Wang,Z.;Xu,M.RoadStructureRefinedCNNforRoadExtractioninAerialImage.IEEEGeosci.RemoteSens.Lett.2017,
14,709–713.[CrossRef]
5. Abdollahi,A.;Pradhan,B.;Shukla,N.ExtractionofRoadFeaturesfromUAVImagesUsingaNovelLevelSetSegmentation
Approach.Int.J.UrbanSci.2019,23,391–405.[CrossRef]
6. Xin,J.;Zhang,X.;Zhang,Z.;Fang,W.RoadExtractionofHigh-ResolutionRemoteSensingImagesDerivedfromDenseUNet.
RemoteSens.2019,11,2499.[CrossRef]
7. Abdollahi,A.;Pradhan,B.;Sharma,G.;Maulud,K.N.A.;Alamri,A.ImprovingRoadSemanticSegmentationUsingGenerative
AdversarialNetwork.IEEEAccess2021,9,64381–64392.[CrossRef]

Sensors2024,24,1708 26of31
8. Lian,R.;Wang,W.;Mustafa,N.;Huang,L.RoadExtractionMethodsinHigh-ResolutionRemoteSensingImages:AComprehen-
siveReview.IEEEJ.Sel.Top.Appl.EarthObs.RemoteSens.2020,13,5489–5507.[CrossRef]
9. Kass,M.;Witkin,A.;Terzopoulos,D.Snakes:ActiveContourModels.Int.J.Comput.Vis.1988,1,321–331.[CrossRef]
10. Miao,Z.;Wang,B.;Shi,W.;Zhang,H.ASemi-AutomaticMethodforRoadCenterlineExtractionfromVhrImages.IEEEGeosci.
RemoteSens.Lett.2014,11,1856–1860.[CrossRef]
11. Gruen,A.;Li,H.RoadExtractionfromAerialandSatelliteImagesbyDynamicProgramming.ISPRSJ.PhotogrammettyRemote
Sens.1995,50,11–20.[CrossRef]
12. Park,S.-R.;Kim,T.Semi-AutomaticRoadExtractionAlgorithmfromIKONOSImagesUsingTemplateMatching.InProceedings
ofthe22ndAsianConferenceonRemoteSensing,Singapore,5–9November2001.
13. Yager,N.;Sowmya,A.SupportVectorMachinesforRoadExtractionfromRemotelySensedImages.InComputerAnalysisofImages
andPatterns;Petkov,N.,Westenberg,M.A.,Eds.;LectureNotesinComputerScience;Springer:Berlin/Heidelberg,Germany,
2003;Volume2756,pp.285–292.ISBN978-3-540-40730-0.
14. Zhang,J.; Chen,L.; Zhuo,L.; Geng,W.; Wang,C.MultipleSaliencyFeaturesBasedAutomaticRoadExtractionfromHigh-
resolutionMultispectralSatelliteImages.Chin.J.Electron.2018,27,133–139.[CrossRef]
15. Yousefi,B.;Mirhassani,S.M.;Marvi,H.ClassificationofRemoteSensingImagesfromUrbanAreasUsingLaplacianImageand
BayesianTheory. InProceedingsoftheInternationalSymposiumonOptomechatronicTechnologies,Lausanne,Switzerland,
8–10October2007;Kofman,J.,LopezDeMeneses,Y.,Kaneko,S.,Perez,C.A.,Coquin,D.,Eds.;SPIE:Bellingham,WA,USA,
2007;p.67180F.
16. Karaman, E.; Çinar, U.; Gedik, E.; Yardımcı, Y.; Halıcı, U. A New Algorithm for Automatic Road Network Extraction in
MultispectralSatelliteImages.InProceedingsofthe4thGEOBIA,RiodeJaneiro,Brazil,7–9May2012.
17. Manandhar,P.;Marpu,P.R.;Aung,Z.SegmentationBasedTraversing-AgentApproachforRoadWidthExtractionfromSatellite
ImagesUsingVolunteeredGeographicInformation.Appl.Comput.Inform.2018,17,131–152.[CrossRef]
18. Tan, Y.-Q.; Gao, S.-H.; Li, X.-Y.; Cheng, M.-M.; Ren, B.VecRoad: Point-BasedIterativeGraphExplorationforRoadGraphs
Extraction.InProceedingsofthe2020IEEE/CVFConferenceonComputerVisionandPatternRecognition(CVPR),Seattle,WA,
USA,13–19June2020;IEEE:Piscataway,NJ,USA,2020;pp.8907–8915.
19. Jia,J.;Sun,H.;Jiang,C.;Karila,K.;Karjalainen,M.;Ahokas,E.;Khoramshahi,E.;Hu,P.;Chen,C.;Xue,T.;etal.ReviewonActive
andPassiveRemoteSensingTechniquesforRoadExtraction.RemoteSens.2021,13,4235.[CrossRef]
20. Liu,P.;Wang,Q.;Yang,G.;Li,L.;Zhang,H.SurveyofRoadExtractionMethodsinRemoteSensingImagesBasedonDeep
Learning.PFG—J.Photogramm.RemoteSens.Geoinf.Sci.2022,90,135–159.[CrossRef]
21. Mnih,V.MachineLearningforAerialImageLabeling.Ph.D.Thesis,UniversityofToronto,Toronto,ON,Canada,2013.
22. Cheng,G.;Wang,Y.;Xu,S.;Wang,H.;Xiang,S.;Pan,C.AutomaticRoadDetectionandCenterlineExtractionviaCascaded
End-to-EndConvolutionalNeuralNetwork.IEEETrans.Geosci.RemoteSens.2017,55,3322–3337.[CrossRef]
23. Demir, I.; Koperski, K.; Lindenbaum, D.; Pang, G.; Huang, J.; Basu, S.; Hughes, F.; Tuia, D.; Raskar, R. DeepGlobe 2018:
AChallengetoParsetheEarththroughSatelliteImages.InProceedingsofthe2018IEEE/CVFConferenceonComputerVision
andPatternRecognitionWorkshops(CVPRW),SaltLakeCity,UT,USA,18–22June2018; IEEE:Piscataway,NJ,USA,2018;
pp.172–17209.
24. Van Etten, A.; Lindenbaum, D.; Bacastow, T.M. SpaceNet: A Remote Sensing Dataset and Challenge Series. arXiv 2019,
arXiv:1807.01232.
25. Bastani,F.;He,S.;Abbar,S.;Alizadeh,M.;Balakrishnan,H.;Chawla,S.;Madden,S.;DeWitt,D.RoadTracer:AutomaticExtraction
ofRoadNetworksfromAerialImages. InProceedingsofthe2018IEEE/CVFConferenceonComputerVisionandPattern
Recognition,SaltLakeCity,UT,USA,18–22June2018;IEEE:Piscataway,NJ,USA,2018;pp.4720–4728.
26. Liu,Y.;Yao,J.;Lu,X.;Xia,M.;Wang,X.;Liu,Y.RoadNet:LearningtoComprehensivelyAnalyzeRoadNetworksinComplex
UrbanScenesfromHigh-ResolutionRemotelySensedImages.IEEETrans.Geosci.RemoteSens.2019,57,2043–2056.[CrossRef]
27. Zhu,Q.;Zhang,Y.;Wang,L.;Zhong,Y.;Guan,Q.;Lu,X.;Zhang,L.;Li,D.AGlobalContext-AwareandBatch-Independent
NetworkforRoadExtractionfromVhrSatelliteImagery.ISPRSJ.Photogramm.RemoteSens.2021,175,353–365.[CrossRef]
28. Ayala,C.;Aranda,C.;Galar,M.Multi-TemporalDataAugmentationforHighFrequencySatelliteImagery:ACaseStudyinSentinel-1and
Sentinel-2BuildingandRoadSegmentation;Jiang,J.,Shaker,A.,Zhang,H.,Eds.;ISPRS:Nice,France,2022;Volume43,pp.25–32.
29. Xu,Z.;Shen,Z.;Li,Y.;Xia,L.;Wang,H.;Li,S.;Jiao,S.;Lei,Y.RoadExtractioninMountainousRegionsfromHigh-Resolution
ImagesBasedonDSDNetandTerrainOptimization.RemoteSens.2021,13,90.[CrossRef]
30. Zhang,T.;Dai,J.;Li,Y.;Zhang,Y.VectorDataPartitionCorrectionMethodSupportedbyDeepLearning.Int.J.RemoteSens.2022,
43,5603–5635.[CrossRef]
31. Han,L.; Hou,L.; Zheng,X.; Ding,Z.; Yang,H.; Zheng,K.SegmentationIsNottheEndofRoadExtraction: AnAll-Visible
DenoisingAutoencoderforConnectedandSmoothRoadReconstruction. IEEETrans. Geosci. RemoteSens. 2023,61,4403818.
[CrossRef]
32. Mnih;Kanade,T.;Kittler,J.;Kleinberg,J.M.;Mattern,F.;Mitchell,J.C.;Naor,M.;Nierstrasz,O.;PanduRangan,C.;Steffen,B.;etal.
LearningtoDetectRoadsinHigh-ResolutionAerialImages.InComputerVision—ECCV2010;Daniilidis,K.,Maragos,P.,Paragios,
N.,Eds.;Springer:Berlin/Heidelberg,Germany,2010;Volume6316,pp.210–223.ISBN978-3-642-15566-6.
33. Wang,J.;Song,J.;Chen,M.;Yang,Z.RoadNetworkExtraction:ANeural-DynamicFrameworkBasedonDeepLearninganda
FiniteStateMachine.Int.J.RemoteSens.2015,36,3144–3169.[CrossRef]

Sensors2024,24,1708 27of31
34. Rezaee,M.;Zhang,Y.RoadDetectionUsingDeepNeuralNetworkinHighSpatialResolutionImages.InProceedingsofthe2017
JointUrbanRemoteSensingEvent(JURSE),Dubai,UnitedArabEmirates,6–8March2017;IEEE:Piscataway,NJ,USA,2017;
pp.1–4.
35. Long,J.;Shelhamer,E.;Darrell,T.FullyConvolutionalNetworksforSemanticSegmentation.arXiv2015,arXiv:1411.4038.
36. Badrinarayanan,V.;Handa,A.;Cipolla,R.SegNet:ADeepConvolutionalEncoder-DecoderArchitectureforRobustSemantic
Pixel-WiseLabelling.arXiv2015,arXiv:1505.07293.
37. Ronneberger, O.; Fischer, P.; Brox, T. U-Net: Convolutional Networks for Biomedical Image Segmentation. arXiv 2015,
arXiv:1505.04597.
38. Zhao,H.;Shi,J.;Qi,X.;Wang,X.;Jia,J.PyramidSceneParsingNetwork.arXiv2017,arXiv:1612.01105.
39. Chaurasia,A.;Culurciello,E.LinkNet:ExploitingEncoderRepresentationsforEfficientSemanticSegmentation.InProceedings
ofthe2017IEEEVisualCommunicationsandImageProcessing(VCIP),St.Petersburg,FL,USA,10–13December2017;pp.1–4.
40. Chen,L.-C.;Zhu,Y.;Papandreou,G.;Schroff,F.;Adam,H.Encoder-DecoderwithAtrousSeparableConvolutionforSemantic
Image Segmentation. In Proceedings of the European Conference on Computer Vision (ECCV), Munich, Germany, 8–14
September2018.
41. Chen,Z.;Wang,C.;Li,J.;Xie,N.;Han,Y.;Du,J.ReconstructionBiasU-NetforRoadExtractionfromOpticalRemoteSensing
Images.IEEEJ.Sel.Top.Appl.EarthObs.RemoteSens.2021,14,2284–2294.[CrossRef]
42. Zhou,L.;Zhang,C.;Wu,M.D-LinkNet:LinkNetwithPretrainedEncoderandDilatedConvolutionforHighResolutionSatellite
ImageryRoadExtraction. InProceedingsofthe2018IEEE/CVFConferenceonComputerVisionandPatternRecognition
Workshops(CVPRW),SaltLakeCity,UT,USA,18–22June2018;IEEE:Piscataway,NJ,USA,2018;pp.192–1924.
43. Milletari,F.;Navab,N.;Ahmadi,S.-A.V-Net:FullyConvolutionalNeuralNetworksforVolumetricMedicalImageSegmentation.
arXiv2016,arXiv:1606.04797.
44. Zhou,Z.;Siddiquee,M.M.R.;Tajbakhsh,N.;Liang,J.UNet++:ANestedU-NetArchitectureforMedicalImageSegmentation.
arXiv2018,arXiv:1807.10165.
45. Qin,X.;Zhang,Z.;Huang,C.;Dehghan,M.;Zaiane,O.R.;Jagersand,M.U2-Net: GoingDeeperwithNestedU-Structurefor
SalientObjectDetection.PatternRecognit.2020,106,107404.[CrossRef]
46. Cao,Y.;Liu,S.;Peng,Y.;Li,J.DenseUNet:DenselyConnectedUNetforElectronMicroscopyImageSegmentation.IETImage
Process.2020,14,2682–2689.[CrossRef]
47. Diakogiannis,F.I.;Waldner,F.;Caccetta,P.;Wu,C.ResUNet-a: ADeepLearningFrameworkforSemanticSegmentationof
RemotelySensedData.ISPRSJ.Photogramm.RemoteSens.2020,162,94–114.[CrossRef]
48. Chen,D.;Hu,F.;Mathiopoulos,P.T.;Zhang,Z.;Peethambaran,J.MC-UNet: MartianCraterSegmentationatSemanticand
InstanceLevelsUsingU-Net-BasedConvolutionalNeuralNetwork.RemoteSens.2023,15,266.[CrossRef]
49. Simonyan,K.;Zisserman,A.VeryDeepConvolutionalNetworksforLarge-ScaleImageRecognition. InProceedingsofthe
InternationalConferenceonLearningRepresentations,SanDiego,CA,USA,7–9May2015.
50. He,K.;Zhang,X.;Ren,S.;Sun,J.DeepResidualLearningforImageRecognition.arXiv2015,arXiv:1512.03385.
51. Chen,L.-C.;Papandreou,G.;Kokkinos,I.;Murphy,K.;Yuille,A.L.SemanticImageSegmentationwithDeepConvolutionalNets
andFullyConnectedCRFs.arXiv2016,arXiv:1412.7062.
52. Chen, L.-C.; Papandreou, G.; Kokkinos, I.; Murphy, K.; Yuille, A.L. DeepLab: Semantic Image Segmentation with Deep
ConvolutionalNets,AtrousConvolution,andFullyConnectedCRFs.arXiv2017,arXiv:1606.00915.[CrossRef]
53. Lan,M.;Zhang,Y.;Zhang,L.;Du,B.GlobalContextBasedAutomaticRoadSegmentationviaDilatedConvolutionalNeural
Network.Inf.Sci.2020,535,156–171.[CrossRef]
54. Gao,C.;Gu,L.;Ren,R.;Jiang,M.DeepLearningCombinedwithTopologyandChannelFeaturesforRoadExtractionfromRemoteSensing
Images;Butler,J.,Xiong,X.,Gu,X.,Eds.;SPIE:Bellingham,WA,USA,2022;Volume12232.
55. Huan,H.;Sheng,Y.;Zhang,Y.;Liu,Y.StripAttentionNetworksforRoadExtraction.RemoteSens.2022,14,4516.[CrossRef]
56. Wu,Q.;Luo,F.;Wu,P.;Wang,B.;Yang,H.;Wu,Y.AutomaticRoadExtractionfromHigh-ResolutionRemoteSensingImages
UsingaMethodBasedonDenselyConnectedSpatialFeature-EnhancedPyramid.IEEEJ.Sel.Top.Appl.EarthObs.RemoteSens.
2020,14,3–17.[CrossRef]
57. Wei,Z.;Zhang,Z.RemoteSensingImageRoadExtractionNetworkBasedonMSPFE-Net.Electronics2023,12,1713.[CrossRef]
58. Gong,Z.;Xu,L.;Tian,Z.;Bao,J.;Ming,D.RoadNetworkExtractionandVectorizationofRemoteSensingImagesBasedon
DeepLearning.InProceedingsofthe2020IEEE5thInformationTechnologyandMechatronicsEngineeringConference(ITOEC),
Chongqing,China,12–14June2020;Xu,B.,Mou,K.,Eds.;IEEE:Piscataway,NJ,USA,2020;pp.303–307.
59. Wang,Q.;Bai,H.;He,C.;Cheng,J.FE-LinkNet:EnhancedD-LinkNetwithAttentionandDenseConnectionforRoadExtraction
inHigh-ResolutionRemoteSensingImages.InProceedingsoftheIGARSS2022-2022IEEEInternationalGeoscienceandRemote
SensingSymposium,KualaLumpur,Malaysia,17–22July2022;IEEE:Piscataway,NJ,USA,2022;pp.3043–3046.
60. Li,H.;Xiong,P.;An,J.;Wang,L.PyramidAttentionNetworkforSemanticSegmentation.arXiv2018,arXiv:1805.10180.
61. Zhang,J.;Li,Y.;Si,Y.;Peng,B.;Xiao,F.;Luo,S.;He,L.ALow-GradeRoadExtractionMethodUsingSDG-DenseNetBasedonthe
FusionofOpticalandSARImagesatDecisionLevel.RemoteSens.2022,14,2870.[CrossRef]
62. Sandler,M.;Howard,A.;Zhu,M.;Zhmoginov,A.;Chen,L.-C.MobileNetV2: InvertedResidualsandLinearBottlenecks. In
Proceedingsofthe2018IEEE/CVFConferenceonComputerVisionandPatternRecognition,SaltLakeCity,UT,USA,18–22June
2018;IEEE:Piscataway,NJ,USA,2018;pp.4510–4520.

Sensors2024,24,1708 28of31
63. Chen,D.;Li,X.;Hu,F.;Mathiopoulos,P.T.;Di,S.;Sui,M.;Peethambaran,J.EDPNet: AnEncoding–DecodingNetworkwith
PyramidalRepresentationforSemanticImageSegmentation.Sensors2023,23,3205.[CrossRef]
64. Hu,J.;Shen,L.;Albanie,S.;Sun,G.;Wu,E.Squeeze-and-ExcitationNetworks.arXiv2019,arXiv:1709.01507.
65. Gao,L.;Wang,J.;Wang,Q.;Shi,W.;Zheng,J.;Gan,H.;Lv,Z.;Qiao,H.RoadExtractionUsingaDualAttentionDilated-LinkNet
BasedonSatelliteImagesandFloatingVehicleTrajectoryData.IEEEJ.Sel.Top.Appl.EarthObs.RemoteSens.2021,14,10428–10438.
[CrossRef]
66. Jie,Y.;He,H.;Xing,K.;Yue,A.;Tan,W.;Yue,C.;Jiang,C.;Chen,X.MECA-Net:AMultiscaleFeatureEncodingandLong-Range
Context-AwareNetworkforRoadExtractionfromRemoteSensingImages.RemoteSens.2022,14,5342.[CrossRef]
67. Bisio,I.;Garibotto,C.;Haleem,H.;Lavagetto,F.;Sciarrone,A.TrafficAnalysisthroughDeep-Learning-BasedImageSegmentation
fromUAVStreaming.IEEEInternetThingsJ.2023,10,6059–6073.[CrossRef]
68. Vaswani,A.;Shazeer,N.;Parmar,N.;Uszkoreit,J.;Jones,L.;Gomez,A.N.;Kaiser,L.;Polosukhin,I.AttentionIsAllYouNeed.
arXiv2023,arXiv:1706.03762.
69. Chen,T.;Jiang,D.;Li,R.SwinTransformersMakeStrongContextualEncodersforVHRImageRoadExtraction.InProceedings
oftheIGARSS2022—2022IEEEInternationalGeoscienceandRemoteSensingSymposium,KualaLumpur,Malaysia,17–22July
2022;IEEE:Piscataway,NJ,USA,2022;pp.3019–3022.
70. Tao,J.;Chen,Z.;Sun,Z.;Guo,H.;Leng,B.;Yu,Z.;Wang,Y.;He,Z.;Lei,X.;Yang,J.Seg-Road:ASegmentationNetworkforRoad
ExtractionBasedonTransformerandCNNwithConnectivityStructures.RemoteSens.2023,15,1602.[CrossRef]
71. Ding,C.;Weng,L.;Xia,M.;Lin,H.Non-LocalFeatureSearchNetworkforBuildingandRoadSegmentationofRemoteSensing
Image.ISPRSInt.J.Geo-Inf.2021,10,245.[CrossRef]
72. Lin,Y.;Xu,D.;Wang,N.;Shi,Z.;Chen,Q.RoadExtractionfromVery-High-ResolutionRemoteSensingImagesviaaNested
SE-DeeplabModel.RemoteSens.2020,12,2985.[CrossRef]
73. Woo,S.;Park,J.;Lee,J.-Y.;Kweon,I.S.CBAM:ConvolutionalBlockAttentionModule.arXiv2018,arXiv:1807.06521.
74. Kong,J.; Zhang,Y.DU-Net-Cloud: ASmartCloud-EdgeApplicationwithanAttentionMechanismandU-NetforRemote
SensingImagesandProcessing.J.CloudComput.-Adv.Syst.Appl.2023,12,1–14.[CrossRef]
75. Dong,S.;Chen,Z.BlockMulti-DimensionalAttentionforRoadSegmentationinRemoteSensingImagery.IEEEGeosci.Remote
Sens.Lett.2022,19,3137551.[CrossRef]
76. Xu,Y.;Chen,H.;Du,C.;Li,J.MSACon:MiningSpatialAttention-BasedContextualInformationforRoadExtraction.IEEETrans.
Geosci.RemoteSens.2022,60,3073923.[CrossRef]
77. Wang,S.;Yang,H.;Wu,Q.;Zheng,Z.;Wu,Y.;Li,J.AnImprovedMethodforRoadExtractionfromHigh-ResolutionRemote-
SensingImagesThatEnhancesBoundaryInformation.Sensors2020,20,2064.[CrossRef]
78. Li,J.;Liu,Y.;Zhang,Y.;Zhang,Y.CascadedAttentiondenseUNet(CADUNet)forRoadExtractionfromVery-High-Resolution
Images.ISPRSInt.J.Geo-Inf.2021,10,329.[CrossRef]
79. Lu,X.;Zhong,Y.;Zheng,Z.ANovelGlobal-AwareDeepNetworkforRoadDetectionofVeryHighResolutionRemoteSensing
Imagery.InProceedingsoftheIGARSS2020—2020IEEEInternationalGeoscienceandRemoteSensingSymposium,Waikoloa,
HI,USA,26September–2October2020;IEEE:Piscataway,NJ,USA,2020;pp.2579–2582.
80. Feng,D.;Shen,X.;Xie,Y.;Liu,Y.;Wang,J.EfficientOccludedRoadExtractionfromHigh-ResolutionRemoteSensingImagery.
RemoteSens.2021,13,4974.[CrossRef]
81. Lu,X.;Zhong,Y.;Zheng,Z.;Zhang,L.GAMSNet:GloballyAwareRoadDetectionNetworkwithMulti-ScaleResidualLearning.
ISPRSJ.Photogramm.RemoteSens.2021,175,340–352.[CrossRef]
82. Zhu,Y.;Long,L.;Wang,J.;Yan,J.;Wang,X.RoadSegmentationfromHigh-FidelityRemoteSensingImagesUsingaContext
InformationCaptureNetwork.Cogn.Comput.2022,14,780–793.[CrossRef]
83. Li,S.;Liao,C.;Ding,Y.;Hu,H.;Jia,Y.;Chen,M.;Xu,B.;Ge,X.;Liu,T.;Wu,D.CascadedResidualAttentionEnhancedRoad
ExtractionfromRemoteSensingImages.ISPRSInt.J.Geo-Inf.2022,11,9.[CrossRef]
84. Bai,X.;Guo,L.;Huo,H.;Zhang,J.;Zhang,Y.;Li,Z.-L.Rse-Net:Road-ShapeEnhancedNeuralNetworkforRoadExtractionin
HighResolutionRemoteSensingImage.Int.J.RemoteSens.2023,44,1–22.[CrossRef]
85. He, L.; Zhu, T.; Lv, M. Retracted: An Early Warning Intelligent Algorithm System for Forest Resource Management and
Monitoring.Comput.Intell.Neurosci.2023,2023,9853814.[CrossRef]
86. Lin,T.-Y.;Dollár,P.;Girshick,R.;He,K.;Hariharan,B.;Belongie,S.FeaturePyramidNetworksforObjectDetection.arXiv2017,
arXiv:1612.03144.
87. Szegedy,C.;Liu,W.;Jia,Y.;Sermanet,P.;Reed,S.;Anguelov,D.;Erhan,D.;Vanhoucke,V.;Rabinovich,A.GoingDeeperwith
Convolutions.arXiv2014,arXiv:1409.4842.
88. Sun,K.;Xiao,B.;Liu,D.;Wang,J.DeepHigh-ResolutionRepresentationLearningforHumanPoseEstimation. arXiv2019,
arXiv:1902.09212.
89. Ren,Y.;Yu,Y.;Guan,H.DA-CapsUNet:ADual-AttentionCapsuleU-NetforRoadExtractionfromRemoteSensingImagery.
RemoteSens.2020,12,2866.[CrossRef]
90. Zhou,M.;Sui,H.;Chen,S.;Wang,J.;Chen,X.BT-RoadNet:ABoundaryandTopologically-AwareNeuralNetworkforRoad
ExtractionfromHigh-ResolutionRemoteSensingImagery.ISPRSJ.Photogramm.RemoteSens.2020,168,288–306.[CrossRef]
91. Ge,Z.;Zhao,Y.;Wang,J.;Wang,D.;Si,Q.DeepFeature-ReviewTransmitNetworkofContour-EnhancedRoadExtractionfrom
RemoteSensingImages.IEEEGeosci.RemoteSens.Lett.2021,19,3001805.[CrossRef]

Sensors2024,24,1708 29of31
92. Li,X.;Wang,Y.;Zhang,L.;Liu,S.;Mei,J.;Li,Y.Topology-EnhancedUrbanRoadExtractionviaaGeographicFeature-Enhanced
Network.IEEETrans.Geosci.RemoteSens.2020,58,8819–8830.[CrossRef]
93. Hu,L.;Niu,C.;Ren,S.;Dong,M.;Zheng,C.;Zhang,W.;Liang,J.DiscriminativeContext-AwareNetworkforTargetExtractionin
RemoteSensingImagery.IEEEJ.Sel.Top.Appl.EarthObs.RemoteSens.2021,15,700–715.[CrossRef]
94. Zou,S.;Xiong,F.;Luo,H.;Lu,J.;Qian,Y.AF-Net:All-ScaleFeatureFusionNetworkforRoadExtractionfromRemoteSensing
Images.InProceedingsofthe2021DigitalImageComputing:TechniquesandApplications(DICTA),GoldCoast,Australia,29
November–1December2021;IEEE:Piscataway,NJ,USA,2021;pp.66–73.
95. Zao,Y.;Chen,H.;Liu,L.;Shi,Z.EnhanceEssentialFeaturesforRoadExtractionfromRemoteSensingImages.InProceedingsof
theIGARSS2022—2022IEEEInternationalGeoscienceandRemoteSensingSymposium,KualaLumpur,Malaysia,17–22July
2022;IEEE:Piscataway,NJ,USA,2022;pp.3023–3026.
96. Yang,M.;Yuan,Y.;Liu,G.SDUNet:RoadExtractionviaSpatialEnhancedandDenselyConnectedUNet.PatternRecognit.2022,
126,108549.[CrossRef]
97. Liu,B.;Ding,J.;Zou,J.;Wang,J.;Huang,S.LDANet:ALightweightDynamicAdditionNetworkforRuralRoadExtractionfrom
RemoteSensingImages.RemoteSens.2023,15,1829.[CrossRef]
98. Cheng,B.;Tian,M.;Jiang,S.;Liu,W.;Pang,Y.Multi-TaskLearningandMultimodalFusionforRoadSegmentation.IEEEAccess
2023,11,18947–18959.[CrossRef]
99. Yan,J.;Chen,Y.;Zheng,J.;Guo,L.;Zheng,S.;Zhang,R.Multi-SourceTimeSeriesRemoteSensingFeatureSelectionandUrban
ForestExtractionBasedonImprovedArtificialBeeColony.RemoteSens.2022,14,4859.[CrossRef]
100. Zhou,M.;Sui,H.;Chen,S.;Chen,X.;Wang,W.;Wang,J.;Liu,J.UGRoadUpd:AnUnchanged-GuidedHistoricalRoadDatabase
UpdatingFrameworkBasedonBi-TemporalRemoteSensingImages. IEEETrans. Intell. Transp. Syst. 2022,23,21465–21477.
[CrossRef]
101. Wu,H.;Zhang,H.;Zhang,X.;Sun,W.;Zheng,B.;Jiang,Y.DeepDualMapper: AGatedFusionNetworkforAutomaticMap
ExtractionUsingAerialImagesandTrajectories.MachineLearningforAerialImageLabeling.arXiv2020,arXiv:2002.06832.
102. Li, Y.; Xiang, L.; Zhang, C.; Jiao, F.; Wu, C.AGuidedDeepLearningApproachforJointRoadExtractionandIntersection
DetectionfromRsImagesandTaxiTrajectories.IEEEJ.Sel.Top.Appl.EarthObs.RemoteSens.2021,14,8008–8018.[CrossRef]
103. Liu,L.;Yang,Z.;Li,G.;Wang,K.;Chen,T.;Lin,L.AerialImagesMeetCrowdsourcedTrajectories:ANewApproachtoRobust
RoadExtraction.IEEETrans.NeuralNetw.Learn.Syst.2022,34,3308–3322.[CrossRef]
104. Tong,Z.;Li,Y.;Zhang,J.;He,L.;Gong,Y.MSFANet:MultiscaleFusionAttentionNetworkforRoadSegmentationofMultispectral
RemoteSensingData.RemoteSens.2023,15,1978.[CrossRef]
105. Zaremba,W.;Sutskever,I.;Vinyals,O.RecurrentNeuralNetworkRegularization.arXiv2015,arXiv:1409.2329.
106. Goodfellow,I.J.;Pouget-Abadie,J.;Mirza,M.;Xu,B.;Warde-Farley,D.;Ozair,S.;Courville,A.;Bengio,Y.GenerativeAdversarial
Networks.arXiv2014,arXiv:1406.2661.[CrossRef]
107. Mirza,M.;Osindero,S.ConditionalGenerativeAdversarialNets.arXiv2014,arXiv:1411.1784.
108. Isola,P.;Zhu,J.-Y.;Zhou,T.;Efros,A.A.Image-to-ImageTranslationwithConditionalAdversarialNetworks.InProceedings
ofthe2017IEEEConferenceonComputerVisionandPatternRecognition(CVPR),Honolulu,HI,USA,21–26July2017;IEEE:
Piscataway,NJ,USA,2017;pp.5967–5976.
109. Yang,C.;Wang,Z.AnEnsembleWassersteinGenerativeAdversarialNetworkMethodforRoadExtractionfromHighResolution
RemoteSensingImagesinRuralAreas.IEEEAccess2020,8,174317–174324.[CrossRef]
110. Cira,C.-I.;Kada,M.;Manso-Callejo,M.;Alcarria,R.;BordelSanchez,B.ImprovingRoadSurfaceAreaExtractionviaSemantic
SegmentationwithConditionalGenerativeLearningforDeepInpaintingOperations.ISPRSInt.J.Geo-Inf.2022,11,43.[CrossRef]
111. Cira, C.-I.; Manso-Callejo, M.; Alcarria, R.; Fernandez Pareja, T.; Bordel Sanchez, B.; Serradilla, F. Generative Learning for
PostprocessingSemanticSegmentationPredictions: ALightweightConditionalGenerativeAdversarialNetworkBasedon
Pix2pixtoImprovetheExtractionofRoadSurfaceAreas.Land2021,10,79.[CrossRef]
112. Chen,W.;Zhou,G.;Liu,Z.;Li,X.;Zheng,X.;Wang,L.NIGAN:AFrameworkforMountainRoadExtractionIntegratingRemote
SensingRoad-SceneNeighborhoodProbabilityEnhancementsandImprovedConditionalGenerativeAdversarialNetwork.
IEEETrans.Geosci.RemoteSens.2022,60,3188908.[CrossRef]
113. Senthilnath,J.;Varia,N.;Dokania,A.;Anand,G.;Benediktsson,J.A.DeepTEC:DeepTransferLearningwithEnsembleClassifier
forRoadExtractionfromUAVImagery.RemoteSens.2020,12,245.[CrossRef]
114. Zhu,J.-Y.;Park,T.;Isola,P.;Efros,A.A.UnpairedImage-to-ImageTranslationUsingCycle-ConsistentAdversarialNetworks.
arXiv2020,arXiv:1703.10593.
115. Cira,C.-I.;Alcarria,R.;Manso-Callejo,M.-A.;Serradilla,F.AFrameworkBasedonNestingofConvolutionalNeuralNetworksto
ClassifySecondaryRoadsinHighResolutionAerialOrthoimages.RemoteSens.2020,12,765.[CrossRef]
116. Szegedy,C.;Ioffe,S.;Vanhoucke,V.;Alemi,A.Inception-v4,Inception-ResNetandtheLearning.arXiv2016,arXiv:1602.07261.
117. Chen,Z.;Fan,W.;Zhong,B.;Li,J.;Du,J.;Wang,C.Corse-to-FineRoadExtractionBasedonLocalDirichletMixtureModelsand
Multiscale-High-OrderDeepLearning.IEEETrans.Intell.Transp.Syst.2020,21,4283–4293.[CrossRef]
118. Li,J.; Meng,Y.; Dorjee,D.; Wei,X.; Zhang,Z.; Zhang,W.AutomaticRoadExtractionfromRemoteSensingImageryUsing
EnsembleLearningandPostprocessing.IEEEJ.Sel.Top.Appl.EarthObs.RemoteSens.2021,14,10535–10547.[CrossRef]
119. Abdollahi,A.;Pradhan,B.;Shukla,N.;Chakraborty,S.;Alamri,A.Multi-ObjectSegmentationinComplexUrbanScenesfrom
High-ResolutionRemoteSensingData.RemoteSens.2021,13,3710.[CrossRef]

Sensors2024,24,1708 30of31
120. Song,H.;Wang,W.;Zhao,S.;Shen,J.;Lam,K.-M.PyramidDilatedDeeperConvLSTMforVideoSalientObjectDetection.In
ComputerVision—ECCV2018; Ferrari,V.,Hebert,M.,Sminchisescu,C.,Weiss,Y.,Eds.; LectureNotesinComputerScience;
SpringerInternationalPublishing:Cham,Switzerland,2018;Volume11215,pp.744–760.ISBN978-3-030-01251-9.
121. Huang, G.; Liu, Z.; van der Maaten, L.; Weinberger, K.Q. Densely Connected Convolutional Networks. arXiv 2018,
arXiv:1608.06993.
122. Cui,F.;Shi,Y.;Feng,R.;Wang,L.;Zeng,T.AGraph-BasedDualConvolutionalNetworkforAutomaticRoadExtractionfrom
HighResolutionRemoteSensingImages.InProceedingsoftheIGARSS2022—2022IEEEInternationalGeoscienceandRemote
SensingSymposium,KualaLumpur,Malaysia,17–22July2022;IEEE:Piscataway,NJ,USA,2022;pp.3015–3018.
123. Sun,Z.;Zhou,W.;Ding,C.;Xia,M.Multi-ResolutionTransformerNetworkforBuildingandRoadSegmentationofRemote
SensingImage.ISPRSInt.J.Geo-Inf.2022,11,165.[CrossRef]
124. Ding, L.; Bruzzone, L.DiResNet: Direction-AwareResidualNetworkforRoadExtractioninVHRRemoteSensingImages.
IEEETrans.Geosci.RemoteSens.2020,59,10243–10254.[CrossRef]
125. Chen,Z.;Wang,C.;Li,J.;Fan,W.;Du,J.;Zhong,B.Adaboost-likeEnd-to-EndMultipleLightweightU-NetsforRoadExtraction
fromOpticalRemoteSensingImages.Int.J.Appl.EarthObs.Geoinf.2021,100,102341.[CrossRef]
126. Wei,Y.;Zhang,K.;Ji,S.SimultaneousRoadSurfaceandCenterlineExtractionfromLarge-ScaleRemoteSensingImagesUsing
CNN-BasedSegmentationandTracing.IEEETrans.Geosci.RemoteSens.2020,58,8919–8931.[CrossRef]
127. Shao,Z.;Zhou,Z.;Huang,X.;Zhang,Y.MRENet:SimultaneousExtractionofRoadSurfaceandRoadCenterlineinComplex
UrbanScenesfromVeryHigh-ResolutionImages.RemoteSens.2021,13,239.[CrossRef]
128. Lu,X.;Zhong,Y.;Zheng,Z.;Chen,D.;Su,Y.;Ma,A.;Zhang,L.CascadedMulti-TaskRoadExtractionNetworkforRoadSurface,
Centerline,andEdgeExtraction.IEEETrans.Geosci.RemoteSens.2022,60,3165817.[CrossRef]
129. Chen,D.;Zhong,Y.;Zheng,Z.;Ma,A.;Lu,X.UrbanRoadMappingBasedonanEnd-to-EndRoadVectorizationMapping
NetworkFramework.ISPRSJ.Photogramm.RemoteSens.2021,178,345–365.[CrossRef]
130. Chen,X.;Sun,Q.;Guo,W.;Qiu,C.;Yu,A.GA-Net:AGeometryPriorAssistedNeuralNetworkforRoadExtraction.Int.J.Appl.
EarthObs.Geoinf.2022,114,103004.[CrossRef]
131. Zao,Y.;Shi,Z.RicherU-Net:LearningMoreDetailsforRoadDetectioninRemoteSensingImages.IEEEGeosci.RemoteSens.Lett.
2022,19,3081774.[CrossRef]
132. Fan,J.;Yang,Z.DeepResidualNetworkBasedRoadDetectionAlgorithmforRemoteSensingImages.InProceedingsofthe2020
5thInternationalConferenceonMechanical,ControlandComputerEngineering(ICMCCE),Harbin,China,25–27December
2020;IEEE:Piscataway,NJ,USA,2020;pp.1723–1726.
133. Abdollahi,A.;Pradhan,B.;Alamri,A.VNet: AnEnd-to-EndFullyConvolutionalNeuralNetworkforRoadExtractionfrom
High-ResolutionRemoteSensingData.IEEEAccess2020,8,179424–179436.[CrossRef]
134. Akhtar, N.; Mandloi, M.DenseResSegnet: ADenseResidualSegnetforRoadDetectionUsingRemoteSensingImages. In
Proceedingsofthe2023InternationalConferenceonMachineIntelligenceforGeoAnalyticsandRemoteSensing(MIGARS),
Hyderabad,India,27–29January2023;Volume1,pp.1–4.
135. Lin,T.-Y.;Goyal,P.;Girshick,R.;He,K.;Dollár,P.FocalLossforDenseObjectDetection.arXiv2018,arXiv:1708.02002.
136. Abdollahi,A.; Pradhan,B.; Alamri,A.RoadVecNet: ANewApproachforSimultaneousRoadNetworkSegmentationand
VectorizationfromAerialandGoogleEarthImageryinaComplexUrbanSet-Up. GiscienceRemoteSens. 2021,58,1151–1174.
[CrossRef]
137. Sushma, B.; Fatimah, B.; Raj, P. Road Segmentation in Aerial Imagery by Deep Neural Networks with 4-Channel Inputs.
InProceedingsofthe2021SixthInternationalConferenceonWirelessCommunications,SignalProcessingandNetworking
(WiSPNET),Chennai,India,25–27March2021;IEEE:Piscataway,NJ,USA,2021;pp.340–344.
138. Yuan,W.;Xu,W.GapLoss:ALossFunctionforSemanticSegmentationofRoadsinRemoteSensingImages.RemoteSens.2022,
14,2422.[CrossRef]
139. Xu,H.;He,H.;Zhang,Y.;Ma,L.;Li,J.AComparativeStudyofLossFunctionsforRoadSegmentationinRemotelySensedRoad
Datasets.Int.J.Appl.EarthObs.Geoinf.2023,116,103159.[CrossRef]
140. Zhang,Y.;Zhu,Q.;Zhong,Y.;Guan,Q.;Zhang,L.;Li,D.AModifiedD-LinkNetwithTransferLearningforRoadExtractionfrom
High-ResolutionRemoteSensing.InProceedingsoftheIGARSS2020-2020IEEEInternationalGeoscienceandRemoteSensing
Symposium,Waikoloa,HI,USA,26September–2October2020;IEEE:Piscataway,NJ,USA,2020;pp.1817–1820.
141. Zhou,Z.-H.ABriefIntroductiontoWeaklySupervisedLearning.Natl.Sci.Rev.2018,5,44–53.[CrossRef]
142. Lian,R.;Huang,L.DeepWindow:SlidingWindowBasedonDeepLearningforRoadExtractionfromRemoteSensingImages.
IEEEJ.Sel.Top.Appl.EarthObs.RemoteSens.2020,13,1905–1916.[CrossRef]
143. Newell,A.;Yang,K.;Deng,J.StackedHourglassNetworksforHumanPoseEstimation.arXiv2016,arXiv:1603.06937.
144. Lian,R.;Huang,L.WeaklySupervisedRoadSegmentationinHigh-ResolutionRemoteSensingImagesUsingPointAnnotations.
IEEETrans.Geosci.RemoteSens.2022,60,3059088.[CrossRef]
145. Wei,Y.;Ji,S.Scribble-BasedWeaklySupervisedDeepLearningforRoadSurfaceExtractionfromRemoteSensingImages.IEEE
Trans.Geosci.RemoteSens.2021,60,3061213.[CrossRef]
146. Zhou,M.;Sui,H.;Chen,S.;Liu,J.;Shi,W.;Chen,X.Large-ScaleRoadExtractionfromHigh-ResolutionRemoteSensingImages
BasedonaWeakly-SupervisedStructuralandOrientationalConsistencyConstraintNetwork.ISPRSJ.Photogramm.RemoteSens.
2022,193,234–251.[CrossRef]

Sensors2024,24,1708 31of31
147. Xiao,R.;Wang,Y.;Tao,C.Fine-GrainedRoadSceneUnderstandingfromAerialImagesBasedonSemisupervisedSemantic
SegmentationNetworks.IEEEGeosci.RemoteSens.Lett.2022,19,3059708.[CrossRef]
148. He,Y.; Wang,J.; Liao,C.; Shan,B.; Zhou,X.ClassHyPer: Classmix-BasedHybridPerturbationsforDeepSemi-Supervised
SemanticSegmentationofRemoteSensingImagery.RemoteSens.2022,14,879.[CrossRef]
149. You,Z.-H.;Wang,J.-X.;Chen,S.-B.;Tang,J.;Luo,B.FMWDCT:ForegroundMixupintoWeightedDual-NetworkCrossTraining
forSemisupervisedRemoteSensingRoadExtraction.IEEEJ.Sel.Top.Appl.EarthObs.RemoteSens.2022,15,5570–5579.[CrossRef]
150. Chen,H.;Li,Z.;Wu,J.;Xiong,W.;Du,C.SemiRoadExNet:ASemi-SupervisedNetworkforRoadExtractionfromRemoteSensing
ImageryviaAdversarialLearning.ISPRSJ.Photogramm.RemoteSens.2023,198,169–183.[CrossRef]
151. Chen,H.;Peng,S.;Du,C.;Li,J.;Wu,S.SW-GAN:RoadExtractionfromRemoteSensingImageryUsingSemi-WeaklySupervised
AdversarialLearning.RemoteSens.2022,14,4145.[CrossRef]
152. Yerram,V.;Takeshita,H.;Iwahori,Y.;Hayashi,Y.;Bhuyan,M.K.;Fukui,S.;Kijsirikul,B.;Wang,A.ExtractionandCalculation
ofRoadwayAreafromSatelliteImagesUsingImprovedDeepLearningModelandPost-Processing. J.Imaging2022,8,124.
[CrossRef][PubMed]
153. Ozturk,O.;Isik,M.S.;Sariturk,B.;Seker,D.Z.GenerationofIstanbulRoadDataSetUsingGoogleMapAPIforDeepLearning-
BasedSegmentation.Int.J.RemoteSens.2022,43,2793–2812.[CrossRef]
154. Zhou,G.; Chen,W.; Gui,Q.; Li,X.; Wang,L.SplitDepth-WiseSeparableGraph-ConvolutionNetworkforRoadExtraction
inComplexEnvironmentsfromHigh-ResolutionRemote-SensingImages. IEEETrans. Geosci. RemoteSens. 2022,60,3128033.
[CrossRef]
155. Li,P.;He,X.;Qiao,M.;Cheng,X.;Li,Z.;Luo,H.;Song,D.;Li,D.;Hu,S.;Li,R.;etal.RobustDeepNeuralNetworksforRoad
ExtractionfromRemoteSensingImages.IEEETrans.Geosci.RemoteSens.2021,59,6182–6197.[CrossRef]
Disclaimer/Publisher’sNote: Thestatements, opinionsanddatacontainedinallpublicationsaresolelythoseoftheindividual
author(s)andcontributor(s)andnotofMDPIand/ortheeditor(s).MDPIand/ortheeditor(s)disclaimresponsibilityforanyinjuryto
peopleorpropertyresultingfromanyideas,methods,instructionsorproductsreferredtointhecontent.