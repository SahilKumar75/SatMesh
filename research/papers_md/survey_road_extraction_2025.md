ISPRS Journal of Photogrammetry and Remote Sensing 228 (2025) 122–140
Contents lists available at ScienceDirect
ISPRS Journal of Photogrammetry and Remote Sensing
journal homepage: www.elsevier.com/locate/isprsjprs
Review Article
Deep learning-based road extraction from remote sensing imagery:
Progress, problems, and perspectives
Xiaoyan Lua,b, Qihao Wenga,b,c,*
aJC STEM Lab of Earth Observations, Department of Land Surveying and Geo-Informatics, The Hong Kong Polytechnic University, Hung Hom, Hong Kong
bResearch Centre for Artificial Intelligence in Geomatics, The Hong Kong Polytechnic University, Hung Hom, Hong Kong
cResearch Institute of Land and Space, The Hong Kong Polytechnic University, Hung Hom, Hong Kong
A R T I C L E I N F O A B S T R A C T
Keywords: Accurate and up-to-date mapping and extraction of road networks are essential for maintaining urban func-
Road segmentation tionality and fostering socioeconomic development, particularly in realizing intelligent transport systems and
Road graph extraction smart city management. Recent advancements in Earth observation and artificial intelligence technologies have
Remote sensing
facilitated more efficient and accurate extraction of road networks from large volumes of remote sensing im-
Deep learning
agery. To investigate these developments, we conducted a comprehensive review of peer-reviewed literature
Sustainable development goals
published between 2017 and 2024, by examining three aspects: data, methods, and applications. This review
revealed key trends in deep learning-based road extraction from remote sensing imagery, including a shift from
raster to vector approaches, from local-scale to global-scale studies, and from pixel-level recognition to practical
applications. Additionally, to achieve high-precision, global-scale road vector extraction, we highlight three
emerging research directions: 1) vectorized extraction of complex viaducts; 2) integration of multimodal remote
sensing data; and 3) the development of novel applications to foster scientific discoveries. Advancing research in
these areas will have profound implications for traffic management, urban planning, disaster response, and the
analysis of socio-economic dynamics. Furthermore, this review collects and shares open-source datasets and code
related to road extraction to support future research, available at https://github.com/RCAIG/GRE-Hub.
1. Introduction 2023). Advancements in remote sensing technologies and computer
vision techniques have significantly enhanced the extraction of global-
The global population is projected to approach 10 billion by 2050 scale road networks from remote sensing imagery with high accuracy
(United-Nations, 2019). This rapid growth is accompanied by acceler- (Lu et al., 2024). Due to the narrow width and long-span characteristics
ated urbanization and the expansion of road infrastructure to facilitate of roads, high-resolution optical satellite imagery serves as the primary
population mobility and meet the growing demand for travel and data source for global road network extraction. Additionally, aerial
transportation (Laurance et al., 2014). Accurate recognition of road imagery serves as a valuable complementary data source.
infrastructure is essential for urban planning, traffic management, Traditional road extraction methods relied on manually designed
disaster response, and environmental monitoring (Liu et al., 2024). feature engineering, such as road shape (Alvarez et al., 2012), geometry
Although open-source datasets, such as gROADS (CIESIN and ITOS, (Liu et al., 2017), and texture (Sghaier and Lepage, 2015), which con-
2013), GRIP (Meijer et al., 2018), and OpenStreetMap (OSM) (Vargas- strained their scalability and applicability in large-scale scenarios. The
Munoz et al., 2020), provide global road mapping, they are often success of AlexNet (Krizhevsky et al., 2012) in the 2012 ImageNet
outdated and spatially incomplete. Furthermore, the efficiency and ac- Challenge marked a pivotal moment in the rise of deep learning.
curacy of crowdsourced road-mapping efforts, such as those of OSM, Consequently, road extraction methods underwent transformative ad-
remain insufficient to meet the practical demands of real-world appli- vancements, beginning with Volodymyr Mnih’s doctoral dissertation
cations. Earth Observation (EO) is increasingly employed for mapping (Mnih, 2013), supervised by Geoffrey Hinton, which pioneered deep
and monitoring dynamic processes on the Earth’s surface (Tuia et al., learning-based approaches to road extraction and introduced the first
* Corresponding author at: JC STEM Lab of Earth Observations, Department of Land Surveying and Geo-Informatics, The Hong Kong Polytechnic University, Hung
Hom, Hong Kong.
E-mail address: qihao.weng@polyu.edu.hk(Q. Weng).
https://doi.org/10.1016/j.isprsjprs.2025.07.013
Received 13 March 2025; Received in revised form 6 June 2025; Accepted 8 July 2025
Available online 15 July 2025
0924-2716/© 2025 The Author(s). Published by Elsevier B.V. on behalf of International Society for Photogrammetry and Remote Sensing, Inc. (ISPRS). This is an
open access article under the CC BY-NC-ND license ( http://creativecommons.org/licenses/by-nc-nd/4.0/ ).

X. Lu and Q. Weng I S P R S J o u r n a l o f P h o t o g r a m m e t r y a n d R e m o t e S e n s i n g 2 28 (2025) 122–140
large-scale Massachusetts Road Dataset. Between 2013 and 2016, road Specifically, road segmentation aims to identify every road pixel within
extraction was primarily dominated by traditional methods (Liu et al., an image, whereas road graph extraction focuses on delineating the
2016; Miao et al., 2015; Wegner et al., 2013), constrained by the limi- nodes and edges that define the road network.
tations of computational resources. Since 2017, the rapid development To address these challenges, recent years have witnessed a surge in
of large-scale road datasets and deep learning-based methods has research advancements leveraging deep learning for road extraction.
significantly advanced road extraction from remote sensing imagery. This progress highlights the need for a comprehensive review of the
Fig. 1presents an overview of key technological advancements in this existing literature. Although several relevant reviews exist (Abdollahi
field. The Massachusetts road dataset (Mnih, 2013) marked the incep- et al., 2020; Chen et al., 2022; Lian et al., 2020; Liu et al., 2022b; Mo
tion of deep learning-based road extraction. The launch of two road et al., 2024; Pruthi and Dhingra, 2023; Wang et al., 2025), they often
extraction competitions, DeepGlobe (Demir et al., 2018) and SpaceNet exhibit one or more of the following limitations: (1) unclear evolu-
(Van Etten et al., 2018), in 2018 substantially accelerated advancements tionary trajectory of deep learning methods for road extraction; (2)
in this field. The MUNO21 dataset (Bastani and Madden, 2021) intro- emphasis on summarizing road segmentation methods while neglecting
duced the new task of road map updating, while GRSet (Lu et al., 2024) the development of road graph extraction; and (3) excessive focus on
represents a global-scale road dataset. D-LinkNet (Zhou et al., 2018), the methodologies, with insufficient exploration of new applications and
champion model of the DeepGlobe competition, has been widely scientific discoveries. An urgent need exists to derive new scientific
adopted in subsequent studies as a robust solution for road segmenta- knowledge from comprehensive road information to enhance the un-
tion. Classical methods for road graph extraction include Deep- derstanding of contemporary urbanization and socio-economic devel-
RoadMapper (Ma´ttyus et al., 2017), RoadTracer (Bastani et al., 2018), opment. Recent advancements in road data, methodologies, and
Seg-Orientation (Batra et al., 2019), and Sat2Graph (He et al., 2020). applications have unlocked new potential to meet these demands,
More recently, SAM-Road (Hetang et al., 2024) fine-tunes the state-of- however, they also present challenges that remain unexamined in pre-
the-art SAM foundation model for road graph extraction. To evaluate vious reviews. In this context, this study employs the data-model-
the quality of road vectorization, the Average Path Length Similarity application framework to provide a comprehensive review of the prog-
(APLS) metric (CosmiQ, 2017) is frequently used as a graph-based per- ress and challenges in deep learning-based road extraction. Based on our
formance measure. As illustrated in Fig. 1, road datasets have progres- findings, we further suggest research directions in this field.
sively evolved toward larger and more global scales. Road graph The structure of this review is as follows: Section 2 provides a
extraction methods have become the prevailing trend, signaling a comprehensive analysis of existing literature; Section 3 discusses the
paradigm shift from raster-based to vector-based approaches. Further- progress in deep learning-based road extraction; Section 4summarizes
more, methods built upon foundation models have emerged. the current trends and identifies key challenges; Section 5 outlines
However, accurately extracting roads from high-resolution remote future research directions; and Section 6concludes this review.
sensing imagery remains a considerable challenge due to the intricate
spatial details and complex backgrounds inherent in these images. For 2. Literature analysis
instance: 1) buildings, trees, and other ground objects introduce occlu-
sions and shadows, causing discontinuities in road extraction; 2) the A systematic literature review was conducted using Google Scholar
textures of surrounding objects often closely resemble road surfaces, (https://scholar.google.com/) to investigate deep learning-based road
leading to a high occurrence of false positives and false negatives; and 3) extraction from remote sensing imagery. The search, spanning the
cross-region road extraction is challenged by significant variations in period from 2017 to 2024, initially yielded thousands of papers.
image radiometric properties, resulting in the omission of road seg- Following a manual exclusion of irrelevant articles, 206 high-quality
ments. Meanwhile, road extraction tasks can be categorized into three papers, along with relevant studies published in Remote Sensing of
types (Liu et al., 2018b): road surface segmentation, centerline extrac- Environment (Slagter et al., 2024), Nature (Engert et al., 2024), and
tion, and boundary detection, as shown in Fig. 2 (a). From the Nature Sustainability (Kleinschroth et al., 2019), were selected for in-
perspective of application demands, each task can be further divided depth analysis and discussion. The 206 high-quality papers were
into two categories: road segmentation (raster) (Sun et al., 2019) and selected based on the reputation of the publication venues and their
road graph extraction (vector) (M´attyus et al., 2017), as shown in Fig. 2 relevance to the research scope, including those published in top-tier
(b). In this study, we adopt the latter categorization approach. computer science conferences, and leading journals in computer
Fig. 1. Key technological advancements in the development of road extraction.
123

X. Lu and Q. Weng I S P R S J o u r n a l o f P h o t o g r a m m e t r y a n d R e m o t e S e n s i n g 2 28 (2025) 122–140
Fig. 2. Visualization of different tasks and forms in road extraction from remote sensing imagery.
science and remote sensing. Each selected paper underwent a rigorous developed countries, road infrastructure is largely well-established, with
review process to ensure alignment with the defined scope of this study. minimal changes over time, resulting in fewer studies in this domain.
For instance, studies on road extraction using only LiDAR data or lane Fig. 5illustrates the publication trends for road segmentation and road
detection with vehicle-mounted cameras were excluded to maintain a graph extraction, revealing that research on road graph extraction
well-defined research scope. constitutes a smaller proportion. This disparity stems from the greater
Fig. 3presents the statistical distribution of publications across top complexity of vector-based extraction relative to segmentation. For
conferences—including ICCV, CVPR, CVPRW, ECCV, WACV, ICRA, instance, complex intersections, including overpasses and multi-level
IROS, AAAI, ICPR, ACM SIGSPATIAL, and IJCAI—and prominent jour- junctions, are treated as regions in segmentation tasks, however, in
nals such as ISPRS, TGRS, JAG, GRSL and JSTARS, as well as a consol- vector extraction, they necessitate precise recognition of road nodes and
idated category labeled “Others” (comprising TIP, TNNLS, PR, RA-L, and their connections. The pie chart in the top-left corner of Fig. 5illustrates
T-IV). The complete names of all journals and conferences are listed in the distribution map of publications on road graph extraction across
Appendix A. The analysis indicates a steady year-over-year increase in different journals and conferences. Most research appears in top-tier
publications, reflecting a growing research contribution to this field, computer vision conferences, underscoring the advanced algorithmic
with significant growth particularly evident in TGRS, GRSL, and demands of road vector extraction. Furthermore, numerous practical
JSTARS. As all three journals are part of IEEE, this trend suggests a applications, including navigation systems, rely on vectorized road data
predominant research focus on algorithm development. Additionally, a to incorporate directional information and additional attributes (e.g.,
notable peak in publications at top conferences was observed in 2018, road types, and speed limits) (Etten, 2020), further increasing the
driven primarily by the DeepGlobe Road Extraction Challenge held at complexity of this task.
CVPRW 2018, which prompted a substantial number of related studies
to be published at that venue. Fig. 4depicts the distribution of publi- 3. Progress
cations by country, showing that China leads research in this field, fol-
lowed by contributions from the United States, Germany, and Canada. This section reviews road extraction from three perspectives: data,
This finding suggests that China has a critical demand for timely and models, and applications. As illustrated in Fig. 6, primary data sources
accurate road information, likely driven by rapid urbanization, infra- for road extraction include high-resolution optical remote sensing im-
structure expansion, and frequent road network updates. In contrast, in ages captured by satellites and aerial platforms, with training samples
Fig. 3. Number of papers on deep learning-based road extraction from remote sensing imagery.
124

X. Lu and Q. Weng I S P R S J o u r n a l o f P h o t o g r a m m e t r y a n d R e m o t e S e n s i n g 2 28 (2025) 122–140
Fig. 4. Number of publications produced by country.
Fig. 5. Number of publications on road segmentation and road graph extraction. Pie chart in the top-left corner represents the distribution map of publications on
road graph extraction.
derived from expert annotation and field surveys. Additionally, several maintaining topological correctness, leading to fragmented or poorly
studies incorporate auxiliary data sources, such as OSM and GPS data, to connected vectorized road outputs. These limitations arise from insuf-
improve the accuracy and robustness of deep learning models. Road ficient global context awareness and challenges in capturing complex
extraction models are typically classified into two categories: road seg- spatial relationships. GNNs address these challenges by explicitly
mentation models and road graph extraction models. Widely adopted modeling roads as nodes and edges, capturing the relational and topo-
architectures include convolutional neural networks (CNNs) logical properties of road networks. This allows for better enforcement
(Krizhevsky et al., 2012), graph neural networks (GNNs) (Wu et al., of connectivity and continuity during inference. Transformer-based
2020), transformer-based architectures (Han et al., 2022), and founda- models further enhance performance by capturing long-range de-
tion models (FMs) (Kirillov et al., 2023). CNNs often struggle with pendencies, whereas foundation models leverage large-scale pretraining
125

X. Lu and Q. Weng I S P R S J o u r n a l o f P h o t o g r a m m e t r y a n d R e m o t e S e n s i n g 2 28 (2025) 122–140
Fig. 6. Road extraction process from data to model and applications.
to generalize across diverse geographic contexts and imaging condi- datasets. To advance deep learning technologies in road extraction,
tions. Key applications of road extraction include map updating (Slagter Geoffrey Hinton’s research group introduced the first large-scale road
et al., 2024), post-disaster accessibility analysis, and socioeconomic dataset, the Massachusetts dataset (Mnih, 2013), comprising high-
development analysis (Xi et al., 2024), contributing to the achievement resolution aerial imagery of Massachusetts, USA. After its release, a
of sustainable development goals (SDGs). The taxonomy of this section is prolonged gap occurred in the publication of similar datasets until 2017.
illustrated in Fig. 7. To facilitate reader comprehension, we also include To highlight road surface segmentation and centerline extraction, Cheng
a selection of classic literature in each section. et al. (2017)introduced the Cheng dataset, which provides labeled road
surfaces and centerlines. However, this dataset, derived from Google
Images, lacks specific location details, making the geographic origin of
3.1. Datasets the data unclear. To advance road vectorization extraction, Bastani et al.
(2018)introduced the RoadTracer dataset, which contains road graph
Table 1 presents a comprehensive summary of open-source road
Fig. 7. Taxonomy of deep learning (DL) based road extraction from remote sensing imagery.
126

X. Lu and Q. Weng                                                                                                                                             I S P  R   S   J  o  u r  n  a l   o  f   P  h  o t  o g  r a  m  m   e  t r y    a n  d    R  e  m  o  t e   S  e  n  s i n  g   2 28 (2025) 122–140
Table 1
Selected open-source road extraction datasets.
Datasets Year Resolution  Buffer width  Size (pixels) Image source Images  Countries Cities Label types Area
(km2)
|     | (m/pixel) | (m) |     |     | (train/val/test) |     |     |     |
| --- | --------- | --- | --- | --- | ---------------- | --- | --- | --- |
Massachusetts  2013 1 7 1500 ×1500 Airborne 1108/14/49 1 >1 Pixel/  2603.25
| (Mnih, 2013) |          |         |           |              |           |                 | vector  |     |
| ------------ | -------- | ------- | --------- | ------------ | --------- | --------------- | ------- | --- |
|              |          | (cid:0) | >600 ×600 |              |           | (cid:0) (cid:0) | >116.12 |     |
| Cheng        | 2017 1.2 |         |           | Google Earth | 160/20/44 |                 | Pixel   |     |
(Cheng et al., 2017)
RoadTracer  2018 0.6 6 1024 ×1024 Google Earth 2880/-/1920 6 40 Pixel/  1811.94
| (Bastani et al., 2018) |     |     |     |     |     |     | vector |     |
| ---------------------- | --- | --- | --- | --- | --- | --- | ------ | --- |
1300 ×1300
SpaceNet3  2018 0.3 2 WorldView3 2213/-/567 4 4 Pixel/  422.84
| (Van Etten et al., 2018) |     |     |     |     |     |     | vector |     |
| ------------------------ | --- | --- | --- | --- | --- | --- | ------ | --- |
DeepGlobe  2018 0.5 (cid:0) 1024 ×1024 DigitalGlobe 4696/-/1530 3 >3 Pixel 1632.11
(Demir et al., 2018)
|                   |        | (cid:0) | 2048 ×2048 |              |          |      |                |     |
| ----------------- | ------ | ------- | ---------- | ------------ | -------- | ---- | -------------- | --- |
| CityScale         | 2020 1 |         |            | Google Earth | 144/9/27 | 1 20 | Pixel/  754.97 |     |
| (He et al., 2020) |        |         |            |              |          |      | Vector         |     |
CHN6-CUG  2021 0.5 (cid:0) 512 ×512 Google Earth 3608/-/903 1 6 Pixel 295.63
(Zhu et al., 2021)
MUNO21  2021 1 (cid:0) 11133 ~  NAIP 80/-/11 1 21 Vector >6000
| (Bastani and Madden,  |     |     | 16520 |     |     |     |     |     |
| --------------------- | --- | --- | ----- | --- | --- | --- | --- | --- |
2021)
|     |     | (cid:0) |     |     | (cid:0) |     |     |     |
| --- | --- | ------- | --- | --- | ------- | --- | --- | --- |
LSRV  2021 0.3 ~ 0.6 16640 ~  Google Earth /-/3 3 3 Pixel 244.99
| (Lu et al., 2021b) |     |     | 23552 |     |     |     |     |     |
| ------------------ | --- | --- | ----- | --- | --- | --- | --- | --- |
GSRV  2024 0.3 ~ 1.2 (cid:0) 1024 ~  Google Earth (cid:0) /-/5743 14 >30 Pixel 2836.38
| (Lu et al., 2024) |     |     | 36,864 |     |     |     |     |     |
| ----------------- | --- | --- | ------ | --- | --- | --- | --- | --- |
GRSet  2024 1 5 1024 ×1024 Google Earth 47,210/-/- 121 121 Pixel 49,503.27
(Lu et al., 2024)
|                    |        | (cid:0) | 2048 ×2048 |              | 2375/339/624 + | (cid:0) (cid:0) |                  |     |
| ------------------ | ------ | ------- | ---------- | ------------ | -------------- | --------------- | ---------------- | --- |
| Global-Scale       | 2024 1 |         |            | Google Earth |                |                 | Pixel/  14545.85 |     |
| (Yin et al., 2024) |        |         |            |              | 130            |                 | Vector           |     |
labels and spans 40 cities across the Netherlands, USA, Canada, UK,  fixed road widths. All the datasets in Table 1 are open-source. The
France, and Japan. Two of the most influential road extraction datasets  TorontoCity (Wang et al., 2016) dataset also includes road data, how-
were introduced through the SpaceNet3 (Van Etten et al., 2018) and  ever, as it is not open-source, specific details are not provided here.
DeepGlobe (Demir et al., 2018) competitions. Both competitions have
garnered global research interest. The SpaceNet3 competition focuses on  3.2. Evaluation metrics
vectorized road extraction, requiring participants to submit vectorized
road outputs. This dataset contains imagery from four cities: Las Vegas
Road extraction evaluation metrics are categorized into pixel-level
(USA), Paris (France), Shanghai (China), and Khartoum (Sudan). The
|     |     |     |     | segmentation  | metrics  | and  graph-based  | vectorization  metrics.  | The  |
| --- | --- | --- | --- | ------------- | -------- | ----------------- | ------------------------ | ---- |
DeepGlobe competition centered on road segmentation, with its dataset
former assesses road segmentation performance, whereas the latter
comprising images from Thailand, Indonesia, and India. evaluates road graph extraction results. Pixel-level segmentation metrics
The CityScale (He et al., 2020) is a dataset developed for city-scale  include precision (P), recall (R), F1 score, and intersection-over-union
vectorized road extraction, covering 20 cities in the USA. Zhu et al.  (IoU), calculated as follows:
(2021)introduced CHN6-CUG, a dataset specifically designed for road
TP
extraction in China, originating from six Chinese cities. Recognizing the  P= (1)
TP+FP
availability of existing global road networks, such as OSM, and the need
for updating current road data, Bastani and Madden (2021)introduced
R= TP
MUNO21, the first road map updating dataset, which tracks road  (2)
TP+FN
changes over eight years across 21 U.S. cities. To evaluate the general-
| ization capability of road extraction models, two specialized datasets  |     |     |     | P×R |     |     |     |     |
| ----------------------------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- |
=2×
were developed: LSRV (Lu et al., 2021b) and GSRV (Lu et al., 2024). The  F1 P+R (3)
LSRV dataset consists of three large-scale images, whereas the GSRV
|     |     |     |     |     | P×R | TP  |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
dataset integrates existing public datasets with manually annotated  IOU= = (4)
|     |     |     |     | R(cid:0) | P×R+P | FN+TP+FP |     |     |
| --- | --- | --- | --- | -------- | ----- | -------- | --- | --- |
large-scale imagery, encompassing images from over 30 cities across 14
countries. This diverse dataset provides a solid foundation for evaluating
where TP (true positives) represents the number of correctly identified
the generalization performance of road extraction models across varied
road pixels, FP (false positives) refers to background pixels incorrectly
geographical and environmental conditions. To establish a robust
identified as roads, and FN (false negatives) denotes road pixels mis-
benchmark for global road extraction, Lu et al. (2024)introduced GRSet,
classified as background.
a road training set comprising 47,210 samples from 121 countries for
The road graph was evaluated using the APLS metric (CosmiQ,
road segmentation. Yin et al. (2024)developed the Global-Scale dataset
2017), initially introduced in the SpaceNet road extraction challenge.
for road graph extraction research, which includes 624 images for in-
The APLS metric quantifies disparities in optimal path lengths between
| domain testing and 130 images for out-of-domain testing. |     |     |     |     |     |     | ʹ   |     |
| -------------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- |
nodes in the ground-truth graph G and the predicted graph G. Ranging
The datasets listed in Table 1that specify road widths indicate that
from 0 (poor) to 1 (perfect), the APLS metric is computed as follows:
the roads have a fixed width. For example, the labels in the Massachu- ( )
|     |     |     |     |     | ∑   |     | ʹ,b ʹ)| |     |
| --- | --- | --- | --- | --- | --- | --- | ------- | --- |
s e t t s ,   R o a d T r a c e r ,  S p a c e N e t 3 ,  a n d  G R S e t  d a t a s e t s   a re  d e r iv e d   fr o m   O S M   ʹ)=1(cid:0) 1 |L(a,b ) (cid:0) L ( a
|     |     |     |     | SP→T (G,G | min | 1,  |     | (5)  |
| --- | --- | --- | --- | --------- | --- | --- | --- | ---- |
d a t a   t h r o u g h   c o r r e ct i o n ,  fi lt e r i n g , a n d  t h e  e s t a b l i s h m e n t  o f  fi x e d  b u f fe r s.  M L ( a, b )
In contrast, datasets without specified widths suggest that the road an- ( )
|     |     |     |     |     | ∑   |     | ʹ,b ʹ)| |     |
| --- | --- | --- | --- | --- | --- | --- | ------- | --- |
n o ta t i o n s   a r e  m a n u a l l y   a n n o t a t e d   w i t h   p i x e l-l e v e l   p r e ci si o n ,   w i th   ʹ,G)=1(cid:0) 1 |L(a,b ) (cid:0) L ( a
|     |     |     |     | ST→P (G | min | 1,  |     | (6)  |
| --- | --- | --- | --- | ------- | --- | --- | --- | ---- |
w id t h s   v a r y in g  ac c o r d i n g   t o  t h e   a c t u al   r o a d   d im e n s i o n s .  N o t a b l y,  t h e  M L (a ʹ, b ʹ )
GSRV dataset contains precisely annotated samples, some of which have
127

X. Lu and Q. Weng I S P R S J o u r n a l o f P h o t o g r a m m e t r y a n d R e m o t e S e n s i n g 2 28 (2025) 122–140
⎛ ⎞
sensing imagery is relatively straightforward, the manual annotation
∑ ⎜ ⎟
APLS= N 1 (y,yʹ) ⎜ ⎝ 1 + 1 1 ⎟ ⎠ (7) p h r ig o h ce -q s u s a is l i b ty o , t h l a c r o g s e tl - y sc a a n le d t d im at e a - s c e o t n s. s u T m o i n a g l , l e p v a i r a ti t c e u l t a h r e ly d fo e r p c e o n n d s e t n ru cy c ti o n n g
SP→T ST→P
extensive labeled data, SSL strategies (Sohn et al., 2020) utilize a small
number of labeled samples, alongside a substantial amount of unlabeled
Where M denotes the number of unique paths, and N represents the data. Among various SSL techniques, pseudo-labeling stands out by
ʹ ʹ
number of images. The nodes a and b are defined as the closest corre- iteratively assigning predicted labels to unlabeled data, thus allowing
sponding nodes in the predicted graph to nodes a and b in the ground- progressive refinement. WSL reduces annotation costs by leveraging
truth graph. L(a,b)and L(a ʹ,b ʹ)represent the shortest path lengths be- sparse labels, such as scribbles (Wei and Ji, 2021) or point (Lian and
ʹ ʹ
tween a and b in the ground-truth graph and between a and b in the Huang, 2021) annotations, thereby reducing labeling efforts while
predicted graph, respectively. The metrics SP→T and ST→P quantify the maintaining competitive performance. However, deep learning models
total difference in shortest path lengths between the ground-truth graph trained under SL, SSL, or WSL paradigms often encounter performance
ʹ
G and the predicted graph G. degradation when applied to data from domains not represented in the
TOPO (Biagioni and Eriksson, 2012) is another widely adopted training set. Such domain gaps—caused by geographic variation, sensor
evaluation metric for road graphs. It works by randomly sampling heterogeneity, and radiometric differences—pose significant challenges
candidate vertices from the ground truth graph and identifying their to model generalization. To address this issue, UDA (Ganin and Lem-
corresponding vertices in the predicted graph. For each matched pair, pitsky, 2015) techniques—most notably adversarial learning
the metric compares the reachable subgraphs originating from the same approaches—integrate unlabeled data from the target domain to
vertex in both graphs and evaluates them using Precision, Recall, and F1 enhance model adaptability and transferability.
score, denoted as: TOPOP, TOPOR, TOPOF1, respectively. This metric Table 2 presents a selection of representative studies on road seg-
emphasizes geometric accuracy and imposes a strong penalty for mentation, chosen based on citation counts (as of February 24, 2025)
incorrect disconnections. and methodological uniqueness.
3.3. Road segmentation 3.3.1. Supervised learning
Geoffrey Hinton’s research group (Mnih, 2013; Mnih and Hinton,
Road segmentation refers to the process of identifying road pixels in 2010) was the first to apply deep neural networks to road extraction,
remote sensing imagery. Based on review of existing literature, road introducing the Massachusetts dataset and pioneering this field. Subse-
segmentation methods can be classified into four categories according to quently, Cheng et al. (2017) released a multi-task road dataset and
their reliance on training samples: supervised learning (SL), semi- proposed a cascaded CNN to simultaneously extract road surfaces and
supervised learning (SSL), weakly supervised learning (WSL), and un- road centerlines. In 2018, the DeepGlobe (Demir et al., 2018) and
supervised domain adaptation (UDA). A highly simplified illustration of SpaceNet (Van Etten et al., 2018) road extraction competitions intro-
the four types of methods is presented in Fig. 8. SL-based road seg- duced two large-scale datasets, attracting global researchers and accel-
mentation methods require substantial volumes of labeled data to train erating advancements in the field. D-LinkNet (Zhou et al., 2018),
deep learning models effectively. While the acquisition of raw remote
Fig. 8. Illustration of various road segmentation methods.
128

X. Lu and Q. Weng I S P R S J o u r n a l o f P h o t o g r a m m e t r y a n d R e m o t e S e n s i n g 2 28 (2025) 122–140
Table 2
Representative road segmentation methods.
Methods Publication Citation Sub-category Highlights
count
Mnih et al. ECCV 2010 803 supervised/ Unsupervised pretraining, neural networks
(Mnih and Hinton, 2010) unsupervised
Mnih et al.(Mnih, 2013) University of Toronto 1050 supervised Massachusetts dataset, machine learning methods
2013
CasNet (Cheng et al., 2017) TGRS 2017 490 supervised Cheng dataset, End-to-end CNN, multi-task
D-LinkNet (Zhou et al., 2018) CVPRW 2018 912 supervised LinkNet with pretrained encoder, dilation convolution
Zhang et al.(Zhang et al., 2018) GRSL 2018 2970 supervised deep residual learning, U-Net
Topology Loss (Mosinska et al., CVPR 2018 292 supervised Topology-aware loss, recursive refinement
2018)
MSMT-RE (Lu et al., 2019) TGRS 2019 169 supervised multi-task, multi-scale, large-scale application
SII-Net (Tao et al., 2019) ISPRS 2019 113 supervised spatial information inference, Conv3d-RNN
Sun et al.(Sun et al., 2019) CVPR 2019 113 supervised Crowdsourced GPS data, 1D transpose convolution
Wei et al. (Wei et al., 2020) TGRS 2020 132 supervised Multi-task, multiple starting points tracing
BT-RoadNet (Zhou et al., 2020) ISPRS 2020 96 supervised Coarse-to-fine architecture, spatial context
RoadDA (Zhang et al., 2021) TGRS 2021 153 UDA GANs-based interdomain adaptation, self-training
ScRoadExtractor (Wei and Ji, 2021) TGRS 2021 117 WSL scribble-based weakly supervised, label propagation
GAMSNet (Lu et al., 2021b) ISPRS 2021 61 supervised LSRV dataset, Global-aware, multi-scale
GOAL (Lu et al., 2021a) ISPRS 2021 35 UDA domain adaptation, global–local adversarial learning
CoANet (Mei et al., 2021) TIP 2021 130 supervised connectivity attention network, strip convolution
CMMPNet (Liu et al., 2022a) TNNLS 2022 22 supervised Aerial images, crowdsourced trajectories, cross-modal message
propagation
SOC-RoadNet (Zhou et al., 2022) ISPRS 2022 25 WSL scribble-labels, road orientation prediction
SemiRoadExNet (Chen et al., 2023b) ISPRS 2023 55 SSL adversarial learning, pseudo labels
Iqbal et al. (Iqbal et al., 2023) ISPRS 2023 8 self- topological constraints, structural conformity loss
supervised
/UDA
Du et al.(Du et al., 2023) ISPRS 2023 15 supervised GF2-FC dataset, local context-aware, non-local
SAM_MLoRA (Lu and Weng, 2024) TGRS 2024 1 supervised/ SAM, fine-tune, two-step optimization
unsupervised
utilizing LinkNet with a pretrained encoder and dilated convolution,
1
∑B
won the championship in the DeepGlobe road extraction competition. Ls =
B
(LBCE (P,Y)+LDCL (P,Y)) (10)
The SpaceNet competition mandated vector-format road predictions and b=1
developed a novel metric: APLS (CosmiQ, 2017), to evaluate the simi-
where P and Y represent the predicted results and ground truth,
larity between ground truth and predicted road graphs. Albu (2018)
respectively. W and H denote the width and height of the image. The
submitted the winning algorithm, which employed an ensemble of deep
learning segmentation encoders and decoders. In the same year, Zhang
output probability at position (i,j)is pij, and the corresponding label is
et al. (2018)were the first to apply deep residual networks (He et al.,
yij.
2016) and U-Net (Ronneberger et al., 2015) to road extraction. Mosinska
et al. (2018) proposed a topology-aware loss function and iterative 3.3.2. Semi-supervised learning
refinement strategy to enhance road connectivity. Since 2019, road In road extraction, SSL has primarily been implemented using con-
extraction research in remote sensing has advanced significantly, sistency regularization and pseudo-labeling techniques. For example,
incorporating methods such as multi-task extraction (Guo et al., 2024; Li You et al. (2022)developed a semi-supervised road extraction method
et al., 2020; Lu et al., 2019; Wei et al., 2020; Yang et al., 2019), modeling integrating dual-network cross-training, foreground pasting, and adap-
contextual information (Bose et al., 2023; Deng et al., 2023; Du et al., tive thresholds to effectively utilize unlabeled data. Yang et al. (2023b)
2023; Hu et al., 2023; Lu et al., 2021b; Tao et al., 2019; Wang et al., introduced a semi-supervised edge-aware road network, which in-
2023a; Yang et al., 2024b; Zhou et al., 2020; Zhu et al., 2021) and tegrates CNN and transformers to enhance road segmentation by
proposed topology-related loss functions (Shit et al., 2021; Xu et al., leveraging multi-scale consistency regularization and road edge infor-
2023a; Xu et al., 2021) to improve road connectivity, leveraging auxil- mation. Huang et al. (2023) proposed a SSL framework that employs
iary data sources such as GPS and OSM for road segmentation (Chen adaptive thresholds based on convergence difficulty to select high-
et al., 2024; Li et al., 2024; Liu et al., 2022a; Sun et al., 2019; Zhang confidence pseudo-labels, thereby improving foreground extraction
et al., 2020). Furthermore, Transformer based architectures (Jiang et al., performance in remote sensing binary segmentation tasks. Chen et al.
2022; Xu et al., 2022) and fine-tuning foundation models (Feng et al., (2023b)presented a generative adversarial network (GAN)-based semi-
2024; Lu and Weng, 2024; Ren et al., 2024) have emerged as viable supervised network for road extraction, enforcing rotation consistency
approaches to road extraction. Among these methods, the commonly of pseudo-labels and ensuring feature distribution consistency between
used supervised loss functions are binary cross-entropy (BCE) and Dice unlabeled and labeled entropy maps. Furthermore, Chen et al. (2023a)
Loss (Milletari et al., 2016), with Dice Loss being particularly effective proposed a semi-supervised knowledge distillation framework incorpo-
for addressing class imbalance, as shown below: rating label diversity progressive learning and a size-variable knowledge
distillation module to map global-scale urban man-made objects,
LBCE (P,Y)=-
∑W ∑H
[yij •logpij +(1-yij )•log(1-pij )] (8) i
t
n
ea
cl
c
u
h
d
e
i
r
n
s
g
e m
bu
i-
i
s
ld
u
i
p
n
e
g
r
s
v i
a
se
n
d
d
f
r
r
o
a
a
m
d
e
s
w
. G
or
a
k
o
in
et
c o
a
r
l
p
.
o
(
r
2
a
0
t
2
in
4
g
)
m
in
u
tr
lt
o
i
d
p
u
le
c e
c
d
o n
a
s is
m
te
e
n
a
c
n
y
-
i=1 j=1
and multitask constraints to enhance road segmentation performance.
2•|P∩Y| These methods typically employ a loss function composed of two com-
LDCL (P,Y)=1-
|P|+|Y|
(9)
ponents: a supervised loss for labeled data (xl, yl) and an unsupervised
loss for unlabeled imagery xu, as shown below:
129

X. Lu and Q. Weng I S P R S J o u r n a l o f P h o t o g r a m m e t r y a n d R e m o t e S e n s i n g 2 28 (2025) 122–140
L=Ll +Lu scribbles), but it generally suffers from weak supervision signals and
=
B
1
∑B
(LBCE (Pl ,Yl )+LDCL (Pl ,Yl ))+
μ
1
B
∑μB
(LBCE (Pu ,Y ̂
u
)
i
w
n
i
c
t
r
h
e
o
a
u
s
t
e d
re q
tr
u
a
ir
in
in
in
g
g
l ab
co
e
m
led
p l
d
ex
a
i
t
t
a
y .
f ro
U
m
D A
th e
e
t
n
a
a
r
b
g
l
e
e
t
s
do
cr
m
o
a
ss
i
-
n
d
.
o
I
m
t u
a
n
in
iq u
tr
e
a
ly
n s
a
f
d
er
-
b=1 b=1 dresses road extraction challenges posed by cross-domain radiometric
+LDCL (Pu ,Y ̂ u )) (11) variations by aligning feature distributions between source and target
domains, allowing models to generalize across diverse geographic and
where μ is the ratio of unlabeled data to labeled data, Pl and Yl represent sensor conditions without manual relabeling. However, its performance
the predicted results and ground truth of the labeled samples xl. Pu and can degrade when domain gaps are large or training is unstable. Overall,
Y ̂ u represent the predicted results and pseudo-label of the unlabeled while SSL, WSL, and UDA all reduce reliance on labeled data, each
samples xu, respectively. approach faces distinct challenges—ranging from pseudo-label quality
and supervision strength to domain shift and training instability.
3.3.3. Weakly-supervised learning
In road extraction tasks, Wei and Ji (2021)proposed a scribble-based 3.4. Road graph extraction
weakly supervised road extraction method that employs a road label
propagation algorithm to propagate semantic information from scribble Road graph extraction involves identifying road nodes and edges
annotations to unlabeled pixels. Lian and Huang (2021) proposed a from remote sensing imagery to generate road vector maps. These maps,
point-based weakly supervised road extraction method that employs a structured as topological directional graphs, serve as a crucial founda-
CNN for point detection, an SVM for point classification, a Gabor filter tion for various remote sensing applications, such as urban planning,
for road potential estimation, and an LBF-Snake model for road region vehicle navigation, and disaster response. By summarizing existing
extraction, significantly reducing annotation costs. SOC-RoadNet (Zhou methods and referencing relevant literature (He et al., 2020), road graph
et al., 2022) was introduced as an end-to-end weakly supervised method extraction techniques can be categorized into two main approaches:
that directly learns road surface features from scribble labels, inte- segmentation-based methods (S) and graph generation methods (G). As
grating structural consistency loss to enhance boundary accuracy and shown in Fig. 9, segmentation-based methods follow a segmentation-
orientation learning to improve road connectivity. In WSL, the lack of vectorization pipeline. Initially, a segmentation network predicts road
precise pixel-level annotations makes models relying solely on BCE Loss segmentation maps. Subsequently, vectorization techniques transform
and Dice Loss prone to unstable optimization, unclear boundary delin- the segmentation maps into road graphs. Graph-based approaches
eation, and incomplete object representations. Therefore, weakly su- enable the direct end-to-end extraction of road graphs G=(V,E)from
pervised loss functions typically incorporate regularization loss, satellite imagery. These approaches are broadly classified into two cat-
boundary loss, and structural consistency loss to impose stronger con- egories: iterative methods and one-shot methods. Iterative methods
straints on road feature learning. (Bastani et al., 2018; Sotiris et al., 2023; Tan et al., 2020; Xu et al., 2022)
sequentially predict the next adjacent vertex based on the current ver-
3.3.4. Unsupervised domain adaptation tex, progressively constructing connected road edges. On the other
To achieve unsupervised learning, Lu et al. (2021a)introduced the hand, one-shot methods (Bahl et al., 2022; He et al., 2020; Hetang et al.,
global–local adversarial learning (GOAL) framework, which leverages 2024; Wang et al., 2023b; Yang et al., 2023a; Yang et al., 2024a) extract
feature space-driven global adversarial learning and local alignment all vertices simultaneously before determining connectivity between
operations to bridge domain gaps, facilitating large-scale road extrac- adjacent vertices.
tion without requiring target domain annotations. Zhang et al. (2021) Table 4highlights representative studies on road graph extraction,
proposed a two-stage UDA framework combining GAN-based inter- focusing primarily on widely cited (as of February 24, 2025) and
domain adaptation and adversarial self-training to address domain shifts extensively discussed methods.
and intradomain discrepancies, thereby enhancing cross-region road
segmentation performance. Current UDA approaches predominantly 3.4.1. Segmentation-based methods
employ adversarial learning to mitigate domain bias between source and The DeepRoadMapper (Ma´ttyus et al., 2017) pioneered the use of a
target domains. The generator G produces samples with data distribu- CNN model to generate road segmentation maps from aerial images.
tions similar to those of the target domain, while the discriminator D Subsequently, it applied complex post-processing steps, including thin-
determines whether the data comes from the source domain or the target ning and the Ramer–Douglas–Peucker algorithm, to extract road graphs.
domain. Through the minimax game, the generated data distribution pz Finally, the A* search algorithm was employed to reason about missing
and the real data distribution pdata tend to become very similar. This connections, producing the final road graph. Batra et al. (2019)utilized
process is described by the following equation: an orientation learning task to enhance the topological accuracy and
connectivity of road networks. Furthermore, a connectivity refinement
V(D,G)=Ex pdata (x) [logD(x)]+Ezpz(z) [log(1(cid:0) D(G(z)))] (12) approach was introduced to connect and refine corrupted road masks,
thereby improving the overall quality of the road graph. CRESIv2 (Etten,
minmaxV(D,G) (13)
G D 2020) employed a segmentation network to process small satellite image
chips, extract road graphs from skeletons, refine nodes and edges,
where D(x)represents the probability that x originates from real data, reconstruct road graph, and infer speed limits or travel time properties
while D(G(z))represents the probability of G(z)derived from a gener- for each roadway.
ated sample. As demonstrated by these methods, the segmentation-based
Table 3summarizes the strengths and weaknesses of different road approach involves a complex processing pipeline and relies on slow,
segmentation approaches. SL methods typically achieve high accuracy intricate, and error-prone post-processing techniques to generate road
within domains where sufficient labeled data are available. However, vector maps. The accuracy of road vector maps is highly dependent on
they struggle with global generalization due to overfitting to local, the quality of the initial road segmentation map, which is susceptible to
region-specific features—making them vulnerable to variations in image challenges such as occlusions, shadows, and varying lighting conditions.
appearance caused by cross-domain differences such as lighting condi- Moreover, predicted segmentation masks frequently fail to accurately
tions, terrain types, and sensor characteristics. SSL alleviates the anno- capture complex road interactions, such as overlapping roads at
tation burden by leveraging unlabeled data, yet its performance is often different elevations. Consequently, segmentation-based road extraction
constrained by the quality of pseudo-labels and class imbalance. WSL methods are gradually being replaced by end-to-end graph-based
reduces labeling costs by using coarse annotations (e.g., points, approaches.
130

X. Lu and Q. Weng I S P R S J o u r n a l o f P h o t o g r a m m e t r y a n d R e m o t e S e n s i n g 2 28 (2025) 122–140
Table 3 and generated road vector graphs with an intersection connection
Strengths and weaknesses of different road segmentation methods. strategy to ensure connectivity. SAM-Road (Hetang et al., 2024)
Methods Strengths Weaknesses extracted large-scale vectorized road graphs from satellite imagery by
fine-tuning SAM to generate road masks and intersections while
SL ● High accuracy on in-domain ● High annotation costs
data ● Poor generalization to new employing a transformer-based GNN to estimate edge probabilities,
● Stable and reliable model domains ensuring efficient and accurate graph prediction.
training Based on the above analysis, Table 5summarizes the strengths and
SSL ● Mitigates dependence on ● Performance heavily depends weaknesses of different road graph extraction methods, which are
extensive labeled data on the quality of pseudo-labels
mainly caused by variations in their processing procedures.
● Enhances model
generalization
WSL ● Reduces annotation cost by ● Lower accuracy due to weak
using weak labels (e.g., points, supervision signals 3.5. Applications
scribbles) ● High training complexity with
the need for tailored learning 3.5.1. Map updating
strategies
Road extraction plays a critical role in map updating by enabling the
UDA ● Reduce annotation costs, only ● Transfer learning is
detection and integration of new or modified road networks into existing
source domain annotation is challenging when domain shift
required. is large. global-scale maps, such as OSM. For example, Fig. 10displays remote
● Strong adaptability to cross- ● Training is often unstable, such sensing imagery of Jiashan County, Zhejiang Province, China, along
domain scenarios. as adversarial learning. with corresponding OSM road data and ground truth road networks.
Although OSM effectively captures major roads, it significantly under-
3.4.2. Graph-based methods represents rural and field roads. In such cases, road graphs extracted
Several well-established iterative methods have been developed. For from remote sensing imagery offer essential supplementary information
instance, RoadTracer (Bastani et al., 2018) pioneered an iterative graph for enhancing and updating OSM maps. Given the need to align newly
construction approach utilizing a CNN-based decision function, though extracted road vectors with existing maps, road graph extraction
it required a manually selected starting node and fixed step sizes. Vec- methods are particularly well-suited for map updating. Bastani and
Road (Tan et al., 2020) introduced a point-based iterative graph Madden (2021), for instance, advocated for a shift from inferring new
exploration scheme to address these limitations by introducing flexible roads to updating existing maps by adding, removing, and adjusting
step sizes and automatic starting nodes, thereby reducing topological road networks. They introduced MUNO21, a novel dataset for road map
errors and manual effort. However, inefficiencies persisted due to the updating that leverages time-series NAIP aerial imagery and OSM data
reliance on patch-based CNN processing. RNGDet (Xu et al., 2022) to track the evolution of physical road networks and street maps over
leveraged Transformer and imitation learning to enable vertex-by- time. On the other hand, Lu et al. (2024)proposed leveraging remote
vertex graph generation, effectively handling complex intersections. sensing imagery and computer vision techniques to enhance existing
Sotiris et al. (2023) applied reinforcement learning and tree-based OSM road data. They introduced a robust global-scale road training
search to sequentially predict road graph topology, improving accu- dataset that significantly improves road mapping completeness and
racy and flexibility in spatial graph prediction, particularly in complex continuity, particularly in rural areas, compared to existing OSM data.
cases with significant occlusions. Despite these advancements, iterative
methods often suffer from significantly low computational efficiency. 3.5.2. Post-disaster accessibility analysis
In comparison, one-shot methods exhibit higher computational ef- The high revisit frequency of satellites enables more frequent and
ficiency and have become the mainstream approach. For example, timely updates than traditional terrestrial methods, which is especially
Sat2Graph (He et al., 2020) introduced graph-tensor encoding (GTE) to critical during natural disasters or other rapidly evolving events. Real-
represent road graphs as tensors, allowing efficient road network graph time road extraction from remote sensing imagery enables effective
mapping and stacked road inference. Bahl et al. (2022) proposed a monitoring of natural disasters, such as floods, earthquakes, and land-
single-shot approach integrating an FCN to identify multiple points of slides, and assessing their impact on transportation infrastructure. This
interest and a GNN to predict their connections, enabling efficient, capability is especially valuable for post-disaster accessibility analysis,
single-pass road graph extraction without iterative processing or starting where timely identification of accessible and disrupted routes is essen-
point generation. TopDiG (Yang et al., 2023a) was introduced as a class- tial for emergency response. By applying road graph extraction methods
agnostic model integrating a topology-focused node detector, dynamic to generate vectorized road representations immediately after a disaster,
graph supervision, and a directional graph generator to extract topo- decision-makers can gain a clearer understanding of the functional
logical graphs. GraphMapper (Wang et al., 2023b) utilized primitive connectivity of the transportation network. As illustrated in Fig. 11,
graph representations and multi-stage learning for unified shape regu- identifying damaged roads after a flood disaster supports the evacuation
larization and topology reconstruction for building and road vector of nearby residents, route planning for rescue teams, and the trans-
extraction from satellite images. IS-RoadDet (Yang et al., 2024a) divided portation of relief supplies. Relevant studies, such as Etten (2020)uti-
road networks into discrete road segments as the smallest topology units lized remote sensing imagery to extract road vectors and infer additional
properties, including speed limits and travel times, by leveraging speed-
Fig. 9. Illustration of different road graph extraction methods.
131

X. Lu and Q. Weng                                                                                                                                             I S P  R   S   J  o  u r  n  a l   o  f   P  h  o t  o g  r a  m  m   e  t r y    a n  d    R  e  m  o  t e   S  e  n  s i n  g   2 28 (2025) 122–140
| Table 4  |     |     | 3.5.3. Urbanization monitoring |     |     |     |
| -------- | --- | --- | ------------------------------ | --- | --- | --- |
Representative road graph extraction methods. Road networks serve as a key indicator of urban expansion, as their
areal growth reflects dynamic changes in land use, infrastructure
| Methods | Publication Citation  | Sub-  Highlights |     |     |     |     |
| ------- | --------------------- | ---------------- | --- | --- | --- | --- |
count category development, and population distribution. Therefore, in such applica-
S G
tions, it is essential to employ road segmentation methods to accurately
DeepRoadMapper ( ICCV 2017 543 √ ​ A* algorithm,  capture the spatial extent of roads and quantify their area over time.
M´attyus et al.,
reasons about  Fig. 12 compares Benin’s road network in 2016 and 2025, clearly
2017) missing  illustrating the trend of urban expansion. Several studies have examined
connections
urban growth patterns. For instance, Liu et al. (2018a)generated multi-
| RoadTracer ( | CVPR 2018 375 | ​ √ RoadTracer  |     |     |     |     |
| ------------ | ------------- | --------------- | --- | --- | --- | --- |
temporal global urban land maps using Landsat imagery from 1990 to
| Bastani et al.,  |     | dataset, iterative  |     |     |     |     |
| ---------------- | --- | ------------------- | --- | --- | --- | --- |
2018) graph  2010 at five-year intervals. Their study utilized artificial elements,
construction including road networks, to analyze urban land expansion in cities such
Seg-Orientation ( CVPR 2019 224 √ ​ Orientation  as Tokyo and Shanghai. OpenEarthMap (Xia et al., 2023), a high-
Batra et al.,  learning,  resolution benchmark dataset where roads form a key category, was
| 2019) |     | connectivity  |                                                                     |     |     |     |
| ----- | --- | ------------- | ------------------------------------------------------------------- | --- | --- | --- |
|       |     | refinement    | introduced for global land cover mapping. It enables automated map- |     |     |     |
√ ​
CRESIv2 (Etten,  WACV 2020 62 Extract road  ping of any location on Earth, supporting decision-making in urban
| 2020) |     | graph, estimates  |     |     |     |     |
| ----- | --- | ----------------- | --- | --- | --- | --- |
monitoring and environmental conservation. Zhou and Weng (2024)
for travel time
introduced Global Urban Mapper, designed to generate high-quality
| VecRoad (Tan  | CVPR 2020 108 | ​ √ point-based   |                  |                     |                 |                  |
| ------------- | ------------- | ----------------- | ---------------- | ------------------- | --------------- | ---------------- |
|               |               |                   | reference  data  | for  global  urban  | mapping  using  | Sentinel-1  and  |
| et al., 2020) |               | iterative graph,  |                  |                     |                 |                  |
flexible step  Sentinel-2 imagery, thereby enabling timely monitoring of ongoing
distance urban expansion and deurbanization. Among its key components, road
​ √
Sat2Graph (He  ECCV 2020 98 CityScale dataset,  networks play a pivotal role in shaping spatial structure and enhancing
| et al., 2020) |     | Graph-tensor  |     |     |     |     |
| ------------- | --- | ------------- | --- | --- | --- | --- |
connectivity.
encoding,
inferring stacked
|               |               | roads              | 4. Trends and challenges |     |     |     |
| ------------- | ------------- | ------------------ | ------------------------ | --- | --- | --- |
| RVMNet (Chen  | ISPRS 2021 36 | ​ √ node proposal  |                          |     |     |     |
| et al., 2021) |               | head, road         |                          |     |     |     |
4.1. From raster to vector
connectivity
refinement
TD-Road (He et al.,  ECCV 2022 9 ​ √ top-down, key  Advancement in remote sensing technologies have enabled the
2022) point and  evolution of road extraction methodologies from pixel-based recogni-
connections  tion to the direct generation of road vector maps. Vector data, composed
prediction
of geometric elements such as points, lines, and polygons, provides su-
| RNGDet (Xu et al.,  | TGRS 2022 51 | ​ √ Transformer,  |     |     |     |     |
| ------------------- | ------------ | ----------------- | --- | --- | --- | --- |
perior storage efficiency and a more accurate representation of topo-
| 2022) |     | decision-making  |     |     |     |     |
| ----- | --- | ---------------- | --- | --- | --- | --- |
agent network logical  relationships  within  road  networks,  such  as  connectivity,
Bahl et al.(Bahl  CVPRW  20 ​ √ Single-shot,  intersections, and loops. As a result, vector-based road mapping from
| et al., 2022) | 2022 | locating points,  |     |     |     |     |
| ------------- | ---- | ----------------- | --- | --- | --- | --- |
remote sensing imagery enhances the efficiency of spatial analysis
link prediction
GraphMapper ( ICCV 2023 4 ​ √ multi-type vector  (Slagter et al., 2024) and route planning (Etten, 2020).
Wang et al.,  mapping,  However, vector road extraction encounters significant challenges
2023b) adaptive shape  due to the complexity of remote sensing imagery and the variability of
regularization
road conditions. As illustrated in Fig. 13, occlusions and shadows from
| Sotiris et al.(Sotiris  | ICCV 2023 2 | ​ √ Reinforcement  |     |     |     |     |
| ----------------------- | ----------- | ------------------ | --- | --- | --- | --- |
buildings and trees, along with variations in road width, material, and
| et al., 2023) |     | learning,  |     |     |     |     |
| ------------- | --- | ---------- | --- | --- | --- | --- |
surface texture, hinder the extraction of continuous road networks.
synthetic road
|     |     | dataset | Moreover, maintaining road connectivity and accurately detecting in- |     |     |     |
| --- | --- | ------- | -------------------------------------------------------------------- | --- | --- | --- |
TopDiG (Yang  CVPR 2023 9 ​ √ class-agnostic,  tersections remain major challenges, particularly in cases of fragmented
| et al., 2023a) |     | topological  | or missing segments. |     |     |     |
| -------------- | --- | ------------ | -------------------- | --- | --- | --- |
directional
graphs
​
SAM-Road (Hetang  CVPRW  18 √ segment anything  4.2. From local to global
| et al., 2024) | 2024 | model (SAM),  |     |     |     |     |
| ------------- | ---- | ------------- | --- | --- | --- | --- |
transformer-
Early road extraction research was limited to local areas due to
based topology
constraints in training datasets and the poor generalization ability of
decoder
IS-RoadDet (Yang  TGRS 2024 0 ​ √ minimum  deep learning models, posing challenges for large-scale road mapping.
et al., 2024a) topology unit,  As depicted in Fig. 14, deep learning models typically perform well on
intersection  the training dataset but show a sharp performance decline when
|     |     | connectivity | encountering domain gaps. |     |     |     |
| --- | --- | ------------ | ------------------------- | --- | --- | --- |
Note: S represents segmentation-based methods, and G represents graph gen- To alleviate this, Bastani et al. (2018)pioneered the development of
eration methods. the RoadTracer dataset, which comprises road network data from 40
cities across six countries. The dataset consists of 25 cities for training
related information embedded in predictive models. These capabilities  and 15 for testing and is designed for road graph extraction and road
are particularly valuable for applications requiring rapid decision-  segmentation, supporting research on large-scale, cross-regional road
making, such as disaster response, where timely and accurate map up- mapping. Recently, constructed a global-scale road training dataset,
GRSet, using satellite imagery and OSM data, covering 49,503.27 km2,
dates are essential. Similarly, the SpaceNet 8 Flood Detection Challenge
(Ha¨nsch et al., 2022) emphasizes detecting flooded vector roads to
along with a global-scale validation dataset, GRSV, which serves as a
assess route accessibility during flood events. This information provides  foundational resource for global road segmentation. Furthermore, they
essential support for disaster assessment and emergency response  introduced a semi-supervised framework to adapt deep learning models
operations. trained on GRSet to diverse geographic regions worldwide. Similarly,
Yin et al. (2024)developed a global dataset using satellite imagery and
132

X. Lu and Q. Weng I S P R S J o u r n a l o f P h o t o g r a m m e t r y a n d R e m o t e S e n s i n g 2 28 (2025) 122–140
Table 5 4.3. From pixels to practices
The strengths and weaknesses of road graph extraction methods.
Methods Strengths Weaknesses Roads, as a fundamental infrastructure, are intrinsically connected to
urban expansion and human activity. New roads are constructed
Segmentation- ● Generate road graph ● Post-processing steps are
wherever human presence expands. Early road extraction tasks pri-
based method based on global complicated;
information ● Road graph depends on the marily focused on mapping, serving geographic surveys of national
● Fast inference speed segmentation map; conditions. The advancement of long-term, wide-coverage, and high-
Iterative methods ● Directly output road ● Iterative leads to slow resolution road extraction using remote sensing imagery has led to
graph processing speeds;
new applications and scientific discoveries. For instance, Xi et al. (2024)
● Road graph is constructed
using local information; developed a comprehensive road network dataset covering 382
● Vertex and edge inference are impoverished counties in China, utilizing deep learning and satellite
determined by their adjacent imagery. The study analyzed the correlation between road length and
vertices; key socioeconomic indicators, such as population, gross domestic
One-shot methods ● Directly output road ● Edge inference dependent on
product (GDP), the added value of the secondary sector of the economy
graph adjacent vertexes
● Fast inference speed (SSE), and the resident savings balance in these counties in 2021. This
dataset can contribute to monitoring SDG progress, such as poverty
eradication and infrastructure accessibility, especially in impoverished
OSM data, covering 13,800 km2, specifically designed for road graph
areas where publicly available road data is incomplete. Similarly, road
extraction. They also introduced SAM-Road++, which incorporates a
development in remote tropical regions is often incomplete or outdated.
node-guided resampling method to mitigate the mismatch issue between
Slagter et al. (2024) introduced a novel method for large-scale moni-
training and inference in SAM-Road (Hetang et al., 2024).
toring of road development in the Congo Basin Forest, utilizing a deep
However, global-scale road extraction remains highly challenging
learning model trained on change ratios derived from Sentinel-1 and
due to substantial variations in data distribution across different regions.
Sentinel-2 imagery. This study mapped 35,944 km of road development
As illustrated in Fig. 15, noticeable differences exist in road attributes
in the Congo Basin Forest between January 2019 and December 2022,
such as radiation, type, material, and scale across regions. These dis-
with at least 78 % of the roads linked to logging activities. These findings
parities pose challenges for a single model to consistently achieve ac-
can help prevent illegal forest activities and aid in assessing ecological
curate road mapping results across diverse regions. To address this,
impacts and carbon emissions associated with logging. Future research
future efforts should focus on developing diverse training datasets and
can explore similar applications, utilizing extracted road data to uncover
enhancing the generalization capability of road extraction models,
new social phenomena and scientific discoveries.
progressively advancing toward global road mapping.
Fig. 10. The road network in Jiashan County, Zhejiang Province, China (Lu et al., 2024).
Fig. 11. Visualization of the 2023 Kalehe flooding event in South Kivu Province, eastern Democratic Republic of the Congo—one of the country’s deadliest disasters
in recent history. Image from Zheng et al. (2024).
133

X. Lu and Q. Weng I S P R S J o u r n a l o f P h o t o g r a m m e t r y a n d R e m o t e S e n s i n g 2 28 (2025) 122–140
Fig. 12. Visualization of the Benin road network in 2016 and 2025 (https://download.geofabrik.de/africa/benin.html).
Fig. 13. Various challenges in road vectorization extraction.
Fig. 14. Deep learning models often fail in the target domain due to limited generalization and distribution shifts between domains. Image from Lu and Weng (2024).
134

X. Lu and Q. Weng I S P R S J o u r n a l o f P h o t o g r a m m e t r y a n d R e m o t e S e n s i n g 2 28 (2025) 122–140
Fig. 15. Diversity in road radiation, type, material, and scale in different regions of the world. Image from the GRSet (Lu et al., 2024).
4.4. Data and computational considerations data augmentation, can reduce computational resource demands while
maintaining accuracy. Furthermore, adjusting batch sizes and
The resolution of remote sensing imagery directly influences the leveraging hardware acceleration (e.g., TPU and GPU parallel
clarity and distinguishability of road structures. In very high-resolution computing) can enhance inference efficiency. Utilizing efficient frame-
(VHR) imagery (e.g., sub-meter resolution), fine road details, such as works (e.g., TensorRT and ONNX Runtime) can further enhance
narrow roads and intersections, are distinctly captured, thereby computational efficiency and minimize resource wastage. Applying
enhancing the accuracy of road extraction. However, VHR imagery re- these methods can reduce computational resource consumption,
quires higher storage capacity and computational resources. Addition- improve system efficiency, and facilitate the practical deployment of
ally, the increased level of detail may introduce more interference, such applications, such as urban planning and emergency response.
as occlusions from buildings, trees, and vehicles, thereby increasing the Table 6highlights how technical obstacles—such as fragmented road
risk of misclassification. In contrast, 1-meter resolution imagery offers a extraction, limited model generalizability, and insufficient road data-
balanced approach to road extraction by reducing noise while main- —directly impact application areas discussed in Section 3.5, including
taining computational efficiency, making it one of the most widely map updating, urbanization monitoring, and post-disaster accessibility
adopted resolutions for road extraction tasks (Bastani and Madden, analysis.
2021; He et al., 2020; Lu et al., 2024; Yin et al., 2024).
Imaging angle is a critical factor in road extraction. Orthorectified 5. Research directions
images provide standardized road structures, making them ideal for
precise, large-scale extraction but at a high cost. Moreover, they struggle 5.1. Vectorization extraction of complex viaducts
to capture multi-level overpasses and underground roads, limiting road
network connectivity analysis. In contrast, oblique images are more Viaduct construction is closely tied to urban transportation planning,
cost-effective and offer richer three-dimensional information, benefiting with their numbers evolving as cities expand. For example, major Chi-
road extraction in complex urban and mountainous areas. However, nese cities such as Beijing, Shanghai, Guangzhou, and Shenzhen have
they are more susceptible to occlusions from trees and high-rise build- numerous viaducts designed to alleviate traffic congestion. Many sec-
ings, leading to road information loss. Additionally, scale variations and tions of China’s highway and high-speed rail networks incorporate
geometric distortions complicate automated road extraction. To viaducts, particularly in mountainous and geologically complex regions.
enhance road extraction accuracy and reliability, future research could Thus, timely updates of vectorized data for newly constructed, modified,
integrate the complementary strengths of orthorectified and oblique or dismantled viaducts are essential for effective transportation network
images. monitoring. As illustrated in Fig. 16, viaducts often exhibit complex
Reliable and efficient global road mapping requires substantial geometric structures, including multiple layers, intersections, and cir-
computational resources, with inference demands closely linked to cular configurations. Accurately capturing their three-dimensional
factors such as image resolution, model complexity, hardware perfor- spatial relationships with traditional two-dimensional vectorization
mance, data preprocessing efficiency, and batch size. Several optimi- methods is particularly challenging, especially in high-density urban
zation strategies can be employed to reduce computational resource areas. Furthermore, viaducts maintain intricate topological relation-
requirements. First, employing lightweight models (e.g., pruning, ships with other transportation infrastructures, such as roads, bridges,
quantization, knowledge distillation) can significantly reduce the and tunnels, making it crucial to preserve these relationships during the
number of parameters and computational complexity, thereby vectorization process. To overcome these challenges, integrating multi-
decreasing resource consumption. Additionally, optimizing data pro- source data—such as remote sensing imagery, LiDAR point clouds, and
cessing techniques, such as adjusting image resolution and employing GPS trajectory data—can be beneficial. However, variations in
135

X. Lu and Q. Weng I S P R S J o u r n a l o f P h o t o g r a m m e t r y a n d R e m o t e S e n s i n g 2 28 (2025) 122–140
Table 6 However, studies exploring the broader implications of road extraction,
Relationship between research trends, challenges and real-world applications. such as its relevance to economic and social development or its potential
Trends Challenges Application problems to uncover new scientific insights, remain relatively limited. In recent
years, several application-oriented studies have emerged, such as Xi
From raster Occlusions, shadows, and road ● Map updating (road
et al. (2024), who analyzed the socioeconomic development of 382
to vector appearance variations often result connectivity)
(Section in fragmented or discontinuous ● Urbanization monitoring counties in China based on road networks extracted from remote sensing
4.1) road extraction (underestimate imagery. Slagter et al. (2024)utilized road information extracted from
urbanization) Sentinel imagery collected over multiple years to monitor changes in the
From local to Significant regional disparities in ● Map updating (limited
Congo Basin Forest roads and analyze their relationship with human
global data distribution severely cross-region
(Section constrain the generalizability of performance) activities. Rather than employing automatic road extraction algorithms,
4.2) models ● Urbanization monitoring Kleinschroth et al. (2019) manually digitized roads from Landsat im-
(inaccurate estimation) agery to investigate road expansion and persistence in the Congo Basin
From pixels Broader applications in ● Urbanization monitoring forests. Likewise, Engert et al. (2024) manually digitized roads from
to practices socioeconomic analysis and (incomplete road data)
(Section environmental monitoring are ● Post-disaster accessibility high-resolution satellite imagery to generate accurate road datasets and
4.3) hindered by the insufficient analysis (error path assess the extent of ghost roads. Despite these advancements, most
availability of timely and analysis) studies remain confined to individual countries or specific research re-
comprehensive road data in gions. Future studies could expand to broader spatial and temporal
remote and impoverished regions
scales, progressing toward global-scale analyses to uncover novel sci-
entific findings.
resolution, coordinate systems, and accuracy among these datasets pose
significant obstacles to data fusion. Consequently, vectorization 6. Conclusions
extraction of complex viaducts remains a critical and challenging
research focus for future studies. Since 2013, deep learning-based road extraction technologies have
advanced rapidly, as artificial intelligence reaches a pivotal milestone
symbolized by advancements in foundation models. Within this context,
5.2. Leveraging foundation models for road extraction
this review examines deep learning-based road extraction from remote
sensing imagery through a comprehensive literature survey and a data-
Recent advancements in foundation models—encompassing both
model-application framework, summarizing publicly available road
vision foundation models (VFMs) and large language models (LLMs)—
datasets, road extraction methodologies, and emerging applications.
have opened up promising new directions for road extraction. Unlike
Our findings indicate that road segmentation datasets and methods
traditional CNNs, VFMs such as the SAM (Kirillov et al., 2023) and
substantially outnumber those dedicated to road vector extraction.
DINOv2 (Oquab et al., 2023) provide highly generalizable visual rep-
However, practical applications, such as map updating, disaster emer-
resentations that can be efficiently adapted for road segmentation (Lu
gency response, and urban monitoring, frequently necessitate road
and Weng, 2024) or road graph extraction (Hetang et al., 2024) with
vector data. Therefore, we emphasize the need for increased focus on
limited supervision. These models demonstrate strong performance in
global-scale road vector extraction, especially in challenging environ-
zero-shot and few-shot learning scenarios, making them particularly
ments such as intricate viaducts, densely forested areas, and remote
valuable for large-scale or cross-domain road extraction. Recent studies
rural regions. In the era of foundation models, the most promising
have also explored integrating LLMs into road topology generation
roadmap to achieve these goals lies in combining large-scale pre-trained
pipelines by modeling spatial dependencies, contextual semantics, and
models with high-quality, task-specific supervised fine-tuning.
auxiliary metadata such as GPS and OSM annotations. For example,
Scientific research extends beyond methodological and algorithmic
LaneGraph2Seq (Peng et al., 2024) employs transformer-based LLMs to
exploration, it also encompasses technology transfer to effectively
derive lane connectivity graphs from raw detections, while multimodal
address pressing real-world challenges. We call for stronger collabora-
LLMs inspired by BLIP-2 (Li et al., 2023) enable direct generation of road
tion between government, industry and academia, as enhanced coop-
graphs from aerial imagery, eliminating the need for intermediate seg-
eration can facilitate the identification of practical demands for needed
mentation masks (Rasal and Boddhu, 2024).
road information and the challenges associated with its application,
Looking forward, the convergence of VFMs and LLMs is poised to
thereby ensuring that research efforts yield tangible societal benefits.
drive a paradigm shift—from conventional vision-based segmentation
For instance, the Hong Kong government has allocated HK$1 billion to
toward reasoning-driven, multimodal scene understanding. This inte- establish the “Smart Traffic Fund”, which supports research and the
gration holds great promise for enabling more robust, scalable, and
implementation of innovative technologies aimed at enhancing
generalizable architectures for automated road mapping and real-time
commuting convenience, optimizing road network efficiency, and
geographic information updating. Nevertheless, several significant
improving driving safety. This initiative underscores the pivotal role of
challenges remain. First, the alignment of visual and textual modalities
road networks in daily life and societal development. From a broader
requires advanced multimodal fusion architectures and access to large-
perspective, this review suggests that future research should extend
scale, high-quality annotated datasets. Second, existing foundation
beyond technical advancements to encompass a deeper and more
models often struggle to achieve topologically accurate representations
comprehensive understanding of the distribution and evolving trends of
in complex scenarios, such as multi-level viaducts, occlusions, or dense
road networks, thereby uncovering new socio-economic patterns and
urban networks. These limitations hinder the precise vectorization and
dynamics and generating valuable scientific insights.
structural interpretation of road scenes. Overcoming these challenges is
essential to fully unlock the potential of foundation models in the
CRediT authorship contribution statement
context of geospatial intelligence and urban infrastructure monitoring.
Xiaoyan Lu: Writing – review & editing, Writing – original draft,
5.3. New applications and scientific discoveries Visualization, Validation, Methodology, Investigation, Formal analysis,
Data curation, Conceptualization. Qihao Weng: Writing – review &
Previous research on road extraction has primarily focused on editing, Supervision, Funding acquisition.
technological advancements, particularly the application of deep
learning techniques to extract roads from remote sensing imagery.
136

X. Lu and Q. Weng I S P R S J o u r n a l o f P h o t o g r a m m e t r y a n d R e m o t e S e n s i n g 2 28 (2025) 122–140
Fig. 16. Complex viaducts in remote sensing imagery. Image from the GSRV dataset (Lu et al., 2024).
Declaration of competing interest Hong Kong SAR Government (P0039329) and Hong Kong Polytechnic
University (P0048671, P0046482 and P0055412). We thank Yuhan
The authors declare that they have no known competing financial Zhou at The Hong Kong Polytechnic University for her suggestions and
interests or personal relationships that could have appeared to influence assistance in improving the figures. The authors are grateful to the ed-
the work reported in this paper. itors and reviewers for their constructive comments and suggestions
which helped improve the manuscript.
Acknowledgement
This research has received funding from Global STEM Professorship,
Appendix A:. Full names and Abbreviations of journals and conferences
Abbreviation Full Name
ICCV International Conference on Computer Vision
CVPR IEEE/CVF Conference on Computer Vision and Pattern Recognition
CVPRW Computer Vision and Pattern Recognition Workshops
ECCV The European Conference on Computer Vision
WACV IEEE/CVF Winter Conference on Applications of Computer Vision
ICRA International Conference on Robotics and Automation
IROS International Conference on Intelligent Robots and Systems
AAAI The Association for the Advancement of Artificial Intelligence
ICPR International Conference on Pattern Recognition
ACM SIGSPATIAL ACM Special Interest Group on Spatial Information
IJCAI International Joint Conferences on Artificial Intelligence
TIP IEEE Transactions on Image Processing
TNNLS IEEE Transactions on Neural Networks and Learning Systems
PR Pattern Recognition
RA-L IEEE Robotics and Automation Letters
T-IV IEEE Transactions on Intelligent Vehicles
ISPRS ISPRS Journal of Photogrammetry and Remote Sensing
TGRS IEEE Transactions on Geoscience and Remote Sensing
JAG International Journal of Applied Earth Observation and Geoinformation
JSTARS IEEE Journal of Selected Topics in Applied Earth Observations and Remote Sensing
GRSL IEEE Geoscience and Remote Sensing Letters
Appendix B:. Open-source codes for road extraction
Methods Website
DeepRoadMapper (Ma´ttyus et al., 2017) https://github.com/mitroadmaps/roadtracer/tree/master/deeproadmapper
RoadTracer (Bastani et al., 2018) https://github.com/mitroadmaps/roadtracer
D-LinkNet (Zhou et al., 2018) https://github.com/zlckanata/DeepGlobe-Road-Extraction-Challenge
Sun et al.(Sun et al., 2019) https://github.com/suniique/Leveraging-Crowdsourced-GPS-Data-for-Road-Extraction-from-Aerial-Imagery
Seg-Orientation (Batra et al., 2019) https://github.com/anilbatra2185/road_connectivity
CRESIv2 (Etten, 2020) https://github.com/avanetten/cresi
Sat2Graph (He et al., 2020) https://github.com/songtaohe/Sat2Graph
VecRoad (Tan et al., 2020) https://github.com/tansor/VecRoad
Wei et al. (Wei et al., 2020) https://github.com/astro-ck/Road-Extraction
RoadDA (Zhang et al., 2021) https://github.com/LANMNG/RoadDA
Bastani et al.(Bastani and Madden, 2021) https://github.com/favyen/muno21
ScRoadExtractor (Wei and Ji, 2021) https://github.com/weiyao1996/ScRoadExtractor
CoANet (Mei et al., 2021) https://github.com/mj129/CoANet
RNGDet (Xu et al., 2022) https://github.com/TonyXuQAQ/RNGDetPlusPlus
(continued on next page)
137

X. Lu and Q. Weng                                                                                                                                             I S P  R   S   J  o  u r  n  a l   o  f   P  h  o t  o g  r a  m  m   e  t r y    a n  d    R  e  m  o  t e   S  e  n  s i n  g   2 28 (2025) 122–140
(continued)
| Methods  Website                                                                  |     |     |     |     |
| --------------------------------------------------------------------------------- | --- | --- | --- | --- |
| CMMPNet (Liu et al., 2022a) https://github.com/liulingbo918/CMMPNet               |     |     |     |     |
| SPIN Road Mapper (Bandara et al., 2022) https://github.com/wgcban/SPIN_RoadMapper |     |     |     |     |
RNGDet++(Xu et al., 2023b)
https://github.com/TonyXuQAQ/RNGDetPlusPlus
| SemiRoadExNet (Chen et al., 2023b) https://github.com/hchen118/SemiRoadExNet |     |     |     |     |
| ---------------------------------------------------------------------------- | --- | --- | --- | --- |
Iqbal et al. (Iqbal et al., 2023) https://github.com/engrjavediqbal/roads-segmentation-adaptation
| MSMDFF-Net (Wang et al., 2024) https://github.com/wycloveinfall/MSMDFF-NET |     |     |     |     |
| -------------------------------------------------------------------------- | --- | --- | --- | --- |
| SAM-Road (Hetang et al., 2024) https://github.com/htcr/sam_road            |     |     |     |     |
| IS-RoadDet (Yang et al., 2024a) https://github.com/WanderRainy/IS-Road     |     |     |     |     |
| GRNetSF_GRSet (Lu et al., 2024) https://github.com/xiaoyan07/GRNet_GRSet   |     |     |     |     |
| SAM_MLoRA (Lu and Weng, 2024) https://github.com/RCAIG/SAM_MLoRA           |     |     |     |     |
| SAM-Road++(Yin et al., 2024) https://github.com/earth-insights/samroadplus |     |     |     |     |
Appendix C:. Performance of different methods on the SpaceNet road dataset
| Methods | TOPOP | TOPOR | TOPOF1 | APLS |
| ------- | ----- | ----- | ------ | ---- |
DeepRoadMapper (Ma´ttyus et al., 2017) 82.79 72.56 77.34 62.26
| D-LinkNet (Zhou et al., 2018)        | 88.42   | 60.06 | 68.80 | 56.93 |
| ------------------------------------ | ------- | ----- | ----- | ----- |
| RoadTracer (Bastani et al., 2018)    | 78.61   | 62.45 | 69.60 | 56.03 |
| Seg-Orientation (Batra et al., 2019) | 81.56   | 71.38 | 76.13 | 58.82 |
| Sat2Graph (He et al., 2020)          | 85.93   | 76.55 | 80.97 | 64.43 |
| GAMSNet (Lu et al., 2021b)           | (cid:0) |       |       | 67.50 |
(cid:0)
| CoANet (Mei et al., 2021)        |         |       |       | 64.57 |
| -------------------------------- | ------- | ----- | ----- | ----- |
| TD-Road (He et al., 2022)        | 84.81   | 77.80 | 81.15 | 65.15 |
| RNGDet (Xu et al., 2022)         | 90.91   | 73.25 | 81.13 | 65.61 |
| RNGDet++(Xu et al., 2023b)       | 91.34   | 75.24 | 82.51 | 67.73 |
| GraphMapper (Wang et al., 2023b) | 90.7    | 84.6  | 87.1  | 68.8  |
| TopoRoad (Zao et al., 2023)      | 87.88   | 81.21 | 83.39 | 66.86 |
| PaLiS (Xu et al., 2024)          | 90.05   | 78.19 | 83.70 | 69.68 |
| SAM-Road (Hetang et al., 2024)   | 93.03   | 70.97 | 80.52 | 71.64 |
| IS-RoadDet (Yang et al., 2024a)  | (cid:0) |       |       | 70.12 |
| SAM-Road++(Yin et al., 2024)     | 93.97   | 72.84 | 82.07 | 74.35 |
Note: The SpaceNet dataset is split into 2040 training and 382 testing images, following He et al. (2020).
Appendix D:. Performance of different methods on the CityScale road dataset
| Methods | TOPOP | TOPOR | TOPOF1 | APLS |
| ------- | ----- | ----- | ------ | ---- |
DeepRoadMapper (Ma´ttyus et al., 2017)
|                                      | 76.54   | 71.25 | 73.80 | 54.32 |
| ------------------------------------ | ------- | ----- | ----- | ----- |
| D-LinkNet (Zhou et al., 2018)        | 78.63   | 48.07 | 57.42 | 54.08 |
| RoadTracer (Bastani et al., 2018)    | 78.00   | 57.44 | 66.16 | 57.29 |
| Seg-Orientation (Batra et al., 2019) | 76.54   | 71.25 | 73.80 | 55.34 |
| Sat2Graph (He et al., 2020)          | 80.70   | 72.28 | 76.26 | 63.14 |
| GAMSNet (Lu et al., 2021b)           | (cid:0) |       |       | 60.09 |
| TD-Road (He et al., 2022)            | 81.94   | 71.63 | 76.43 | 65.74 |
| RNGDet (Xu et al., 2022)             | 85.97   | 69.78 | 76.87 | 65.75 |
| RNGDet++(Xu et al., 2023b)           | 85.65   | 72.58 | 78.44 | 67.76 |
| GraphMapper (Wang et al., 2023b)     | 89.6    | 82.6  | 85.6  | 68.0  |
| TopoRoad (Zao et al., 2023)          | 79.89   | 78.10 | 78.82 | 71.18 |
| PaLiS (Xu et al., 2024)              | 86.36   | 73.16 | 79.08 | 68.12 |
| SAM-Road (Hetang et al., 2024)       | 90.47   | 67.69 | 77.23 | 68.37 |
| IS-RoadDet (Yang et al., 2024a)      | (cid:0) |       |       | 69.36 |
SAM-Road++(Yin et al., 2024)
|     | 89.08 | 74.07 | 80.66 | 69.55 |
| --- | ----- | ----- | ----- | ----- |
Note: The CityScale dataset is split into 144 training and 27 testing images, following He et al. (2020).
References Bastani, F., He, S., Abbar, S., Alizadeh, M., Balakrishnan, H., Chawla, S., Madden, S.,
DeWitt, D., 2018. RoadTracer: Automatic extraction of road networks from aerial
images. In: Proceedings of the IEEE Conference on Computer Vision and Pattern
Abdollahi, A., Pradhan, B., Shukla, N., Chakraborty, S., Alamri, A., 2020. Deep learning  Recognition, pp. 4720–4728.
approaches applied to remote sensing datasets for road extraction: a state-of-the-art
Bastani, F., Madden, S., 2021. Beyond road extraction: a dataset for map update using
review. Remote Sens. (Basel) 12 (9), 1444.
Albu, 2018. SpaceNet round 3 winner: albu’s implementation. https://github.com/Space  aerial images. In: Proceedings of the IEEE/CVF International Conference on
Computer Vision, pp. 11905–11914.
NetChallenge/RoadDetector/tree/master/albu-solution.
Batra, A., Singh, S., Pang, G., Basu, S., Jawahar, C., Paluri, M., 2019. Improved road
Alvarez, J.M., Gevers, T., Diego, F., Lopez, A.M., 2012. Road geometry classification by  connectivity by joint learning of orientation and segmentation. In: Proceedings of the
adaptive shape models. IEEE Trans. Intell. Transp. Syst. 14 (1), 459–468.
IEEE/CVF Conference on Computer Vision and Pattern Recognition,
Bahl, G., Bahri, M., Lafarge, F., 2022. Single-shot end-to-end road graph extraction. In:  pp. 10385–10393.
Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern
Biagioni, J., Eriksson, J., 2012. Inferring road maps from global positioning system
Recognition, pp. 1403–1412.
traces: Survey and comparative evaluation. Transp. Res. Rec. 2291 (1), 61–71.
Bandara, W.G.C., Valanarasu, J.M.J., Patel, V.M., 2022. SPIN Road Mapper: Extracting  Bose, S., Chowdhury, R.S., Pal, D., Bose, S., Banerjee, B., Chaudhuri, S., 2023. Multiscale
roads from aerial images via spatial and interaction space graph reasoning for
probability map guided index pooling with attention-based learning for road and
autonomous driving. In: 2022 International Conference on Robotics and Automation  building segmentation. ISPRS J. Photogramm. Remote Sens. 206, 132–148.
(ICRA). IEEE, pp. 343–350.
138

X. Lu and Q. Weng I S P R S J o u r n a l o f P h o t o g r a m m e t r y a n d R e m o t e S e n s i n g 2 28 (2025) 122–140
Chen, D., Ma, A., Zhong, Y., 2023a. Semi-supervised knowledge distillation framework Krizhevsky, A., Sutskever, I., Hinton, G.E., 2012. ImageNet classification with deep
for global-scale urban man-made object remote sensing mapping. Int. J. Appl. Earth convolutional neural networks. Advances in Neural Information Processing Systems
Obs. Geoinf. 122, 103439. 25.
Chen, D., Zhong, Y., Zheng, Z., Ma, A., Lu, X., 2021. Urban road mapping based on an Laurance, W.F., Clements, G.R., Sloan, S., O’connell, C.S., Mueller, N.D., Goosem, M.,
end-to-end road vectorization mapping network framework. ISPRS J. Photogramm. Venter, O., Edwards, D.P., Phalan, B., Balmford, A., 2014. A global strategy for road
Remote Sens. 178, 345–365. building. Nature 513 (7517), 229–232.
Chen, H., Li, Z., Wu, J., Xiong, W., Du, C., 2023b. SemiRoadExNet: a semi-supervised Li, B., Gao, J., Chen, S., Lim, S., Jiang, H., 2024. DF-DRUNet: a decoder fusion model for
network for road extraction from remote sensing imagery via adversarial learning. automatic road extraction leveraging remote sensing images and GPS trajectory
ISPRS J. Photogramm. Remote Sens. 198, 169–183. data. Int. J. Appl. Earth Obs. Geoinf. 127, 103632.
Chen, X., Yu, A., Sun, Q., Guo, W., Xu, Q., Wen, B., 2024. Updating road maps at city Li, J., Li, D., Savarese, S., Hoi, S., 2023. BLIP-2: Bootstrapping language-image pre-
scale with remote sensed images and existing vector maps. IEEE Trans. Geosci. training with frozen image encoders and large language models. International
Remote Sens. 62, 1–21. Conference on Machine Learning. PMLR 19730–19742.
Chen, Z., Deng, L., Luo, Y., Li, D., Junior, J.M., Gonçalves, W.N., Nurunnabi, A.A.M., Li, R., Gao, B., Xu, Q., 2020. Gated auxiliary edge detection task for road extraction with
Li, J., Wang, C., Li, D., 2022. Road extraction in remote sensing data: a survey. Int. J. weight-balanced loss. IEEE Geosci. Remote Sens. Lett. 18 (5), 786–790.
Appl. Earth Obs. Geoinf. 112, 102833. Lian, R., Huang, L., 2021. Weakly supervised road segmentation in high-resolution
Cheng, G., Wang, Y., Xu, S., Wang, H., Xiang, S., Pan, C., 2017. Automatic road detection remote sensing images using point annotations. IEEE Trans. Geosci. Remote Sens. 60,
and centerline extraction via cascaded end-to-end convolutional neural network. 1–13.
IEEE Trans. Geosci. Remote Sens. 55 (6), 3322–3337. Lian, R., Wang, W., Mustafa, N., Huang, L., 2020. Road extraction methods in high-
CIESIN, ITOS, 2013. Global Roads Open Access Data Set, Version 1 (gROADSv1). resolution remote sensing images: a comprehensive review. IEEE J. Sel. Top. Appl.
Palisades, NY: NASA Socioeconomic Data and Applications Center (SEDAC). Earth Obs. Remote Sens. 13, 5489–5507.
CosmiQ, 2017. Average Path Length Similarity (APLS) metric: https://github.com/ Liu, J., Qin, Q., Li, J., Li, Y., 2017. Rural road extraction from high-resolution remote
CosmiQ/apls. sensing images based on geometric feature inference. ISPRS Int. J. Geo Inf. 6 (10),
Demir, I., Koperski, K., Lindenbaum, D., Pang, G., Huang, J., Basu, S., Hughes, F., 314.
Tuia, D., Raskar, R., 2018. DeepGlobe 2018: a challenge to parse the earth through Liu, L., Yang, Z., Li, G., Wang, K., Chen, T., Lin, L., 2022a. Aerial images meet
satellite images. In: Proceedings of the IEEE Conference on Computer Vision and crowdsourced trajectories: a new approach to robust road extraction. IEEE Trans.
Pattern Recognition Workshops, pp. 172–181. Neural Networks Learn. Syst. 34 (7), 3308–3322.
Deng, F., Luo, W., Ni, Y., Wang, X., Wang, Y., Zhang, G., 2023. UMiT-Net: a U-shaped Liu, P., Wang, Q., Yang, G., Li, L., Zhang, H., 2022b. Survey of road extraction methods in
mix-transformer network for extracting precise roads using remote sensing images. remote sensing images based on deep learning. PFG–Journal of Photogrammetry,
IEEE Trans. Geosci. Remote Sens. 61, 1–13. Remote Sensing and Geoinformation. Science 90 (2), 135–159.
Du, Y., Sheng, Q., Zhang, W., Zhu, C., Li, J., Wang, B., 2023. From local context-aware to Liu, R., Song, J., Miao, Q., Xu, P., Xue, Q., 2016. Road centerlines extraction from high
non-local: a road extraction network via guidance of multi-spectral image. ISPRS J. resolution images based on an improved directional segmentation and road
Photogramm. Remote Sens. 203, 230–245. probability. Neurocomputing 212, 88–95.
Engert, J.E., Campbell, M.J., Cinner, J.E., Ishida, Y., Sloan, S., Supriatna, J., Alamgir, M., Liu, R., Wu, J., Lu, W., Miao, Q., Zhang, H., Liu, X., Lu, Z., Li, L., 2024. A review of deep
Cislowski, J., Laurance, W.F., 2024. Ghost roads and the destruction of Asia-Pacific learning-based methods for road extraction from high-resolution remote sensing
tropical forests. Nature 629 (8011), 370–375. images. Remote Sens. (Basel) 16 (12), 2056.
Etten, A.V., 2020. City-scale road extraction from satellite imagery v2: Road speeds and Liu, X., Hu, G., Chen, Y., Li, X., Xu, X., Li, S., Pei, F., Wang, S., 2018a. High-resolution
travel times. In: Proceedings of the IEEE/CVF Winter Conference on Applications of multi-temporal mapping of global urban land using Landsat images based on the
Computer Vision, pp. 1786–1795. Google Earth Engine Platform. Remote Sens. Environ. 209, 227–239.
Feng, W., Guan, F., Sun, C., Xu, W., 2024. Road-SAM: Adapting the segment anything Liu, Y., Yao, J., Lu, X., Xia, M., Wang, X., Liu, Y., 2018b. RoadNet: Learning to
model to road extraction from large very-high-resolution optical remote sensing comprehensively analyze road networks in complex urban scenes from high-
images. IEEE Geosci. Remote Sens. Lett. 21, 1–5. resolution remotely sensed images. IEEE Trans. Geosci. Remote Sens. 57 (4),
Ganin, Y., Lempitsky, V., 2015. Unsupervised domain adaptation by backpropagation. 2043–2056.
International Conference on Machine Learning. PMLR 1180–1189. Lu, X., Weng, Q., 2024. Multi-LoRA fine-tuned segment anything model for urban man-
Gao, L., Zhou, Y., Tian, J., Cai, W., Lv, Z., 2024. MCMCNet: a semi-supervised road made object extraction. IEEE Trans. Geosci. Remote Sens. 62, 1–19.
extraction network for high-resolution remote sensing images via multiple Lu, X., Zhong, Y., Zheng, Z., Liu, Y., Zhao, J., Ma, A., Yang, J., 2019. Multi-scale and
consistency and multi-task constraints. IEEE Trans. Geosci. Remote Sens. 62, 1–16. multi-task deep learning framework for automatic road extraction. IEEE Trans.
Guo, H., Su, X., Wu, C., Du, B., Zhang, L., 2024. Building-road collaborative extraction Geosci. Remote Sens. 57 (11), 9362–9377.
from remote sensing images via cross-task and cross-scale interaction. IEEE Trans. Lu, X., Zhong, Y., Zheng, Z., Wang, J., 2021a. Cross-domain road detection based on
Geosci. Remote Sens. 62, 1–16. global-local adversarial learning framework from very high resolution satellite
Han, K., Wang, Y., Chen, H., Chen, X., Guo, J., Liu, Z., Tang, Y., Xiao, A., Xu, C., Xu, Y., imagery. ISPRS J. Photogramm. Remote Sens. 180, 296–312.
2022. A survey on vision transformer. IEEE Trans. Pattern Anal. Mach. Intell. 45 (1), Lu, X., Zhong, Y., Zheng, Z., Wang, J., Chen, D., Su, Y., 2024. Global road extraction
87–110. using a pseudo-label guided framework: from benchmark dataset to cross-region
Ha¨nsch, R., Arndt, J., Lunga, D., Gibb, M., Pedelose, T., Boedihardjo, A., Petrie, D., semi-supervised learning. Geo-spatial Inf. Sci. 1–19.
Bacastow, T.M., 2022. SpaceNet 8 - the detection of flooded roads and buildings. In: Lu, X., Zhong, Y., Zheng, Z., Zhang, L., 2021b. GAMSNet: Globally aware road detection
Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern network with multi-scale residual learning. ISPRS J. Photogramm. Remote Sens.
Recognition, pp. 1472–1480. 175, 340–352.
He, K., Zhang, X., Ren, S., Sun, J., 2016. Deep residual learning for image recognition. In: M´attyus, G., Luo, W., Urtasun, R., 2017. DeepRoadMapper: Extracting road topology
Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition, from aerial images. In: Proceedings of the IEEE International Conference on
pp. 770–778. Computer Vision, pp. 3438–3446.
He, S., Bastani, F., Jagwani, S., Alizadeh, M., Balakrishnan, H., Chawla, S., Elshrif, M.M., Mei, J., Li, R.-J., Gao, W., Cheng, M.-M., 2021. CoANet: Connectivity attention network
Madden, S., Sadeghi, M.A., 2020. Sat2Graph: Road graph extraction through graph- for road extraction from satellite imagery. IEEE Trans. Image Process. 30,
tensor encoding. Computer Vision–ECCV 2020: 16th European Conference, Glasgow, 8540–8552.
UK, August 23–28, 2020, Proceedings, Part XXIV 16. Springer, pp. 51-67. Meijer, J.R., Huijbregts, M.A., Schotten, K.C., Schipper, A.M., 2018. Global patterns of
He, Y., Garg, R., Chowdhury, A.R., 2022. TD-Road: top-down road network extraction current and future road infrastructure. Environ. Res. Lett. 13 (6), 064006.
with holistic graph construction. European Conference on Computer Vision. Springer Miao, Z., Shi, W., Samat, A., Lisini, G., Gamba, P., 2015. Information fusion for urban
562–577. road extraction from VHR optical satellite images. IEEE J. Sel. Top. Appl. Earth Obs.
Hetang, C., Xue, H., Le, C., Yue, T., Wang, W., He, Y., 2024. Segment anything model for Remote Sens. 9 (5), 1817–1829.
road network graph extraction. In: Proceedings of the IEEE/CVF Conference on Milletari, F., Navab, N., Ahmadi, S.-A., 2016. V-Net: fully convolutional neural networks
Computer Vision and Pattern Recognition, pp. 2556–2566. for volumetric medical image segmentation. In: 2016 Fourth International
Hu, J., Gao, J., Yuan, Y., Chanussot, J., Wang, Q., 2023. LGNet: Location-guided network Conference on 3D Vision (3DV). IEEE, pp. 565–571.
for road extraction from satellite images. IEEE Trans. Geosci. Remote Sens. 61, 1–12. Mnih, V., 2013. Machine learning for aerial image labeling. University of Toronto
Huang, W., Shi, Y., Xiong, Z., Zhu, X.X., 2023. AdaptMatch: Adaptive matching for (Canada).
semisupervised binary segmentation of remote sensing images. IEEE Trans. Geosci. Mnih, V., Hinton, G.E., 2010. Learning to detect roads in high-resolution aerial images.
Remote Sens. 61, 1–16. Computer Vision–ECCV 2010: 11th European Conference on Computer Vision,
Iqbal, J., Masood, A., Sultani, W., Ali, M., 2023. Leveraging topology for domain Heraklion, Crete, Greece, September 5-11, 2010, Proceedings, Part VI 11. Springer,
adaptive road segmentation in satellite and aerial imagery. ISPRS J. Photogramm. pp. 210-223.
Remote Sens. 206, 106–117. Mo, S., Shi, Y., Yuan, Q., Li, M., 2024. A survey of deep learning road extraction
Jiang, X., Li, Y., Jiang, T., Xie, J., Wu, Y., Cai, Q., Jiang, J., Xu, J., Zhang, H., 2022. algorithms using high-resolution remote sensing images. Sensors 24 (5), 1708.
RoadFormer: Pyramidal deformable vision transformers for road network extraction Mosinska, A., Marquez-Neila, P., Kozin´ski, M., Fua, P., 2018. Beyond the pixel-wise loss
with remote sensing images. Int. J. Appl. Earth Obs. Geoinf. 113, 102987. for topology-aware delineation. In: Proceedings of the IEEE Conference on Computer
Kirillov, A., Mintun, E., Ravi, N., Mao, H., Rolland, C., Gustafson, L., Xiao, T., Vision and Pattern Recognition, pp. 3136–3145.
Whitehead, S., Berg, A.C., Lo, W.-Y., 2023. Segment anything. In: Proceedings of the Oquab, M., Darcet, T., Moutakanni, T., Vo, H., Szafraniec, M., Khalidov, V., Fernandez,
IEEE/CVF International Conference on Computer Vision, pp. 4015–4026. P., Haziza, D., Massa, F., El-Nouby, A., 2023. Dinov2: Learning robust visual features
Kleinschroth, F., Laporte, N., Laurance, W.F., Goetz, S.J., Ghazoul, J., 2019. Road without supervision. arXiv preprint arXiv:2304.07193.
expansion and persistence in forests of the Congo Basin. Nat. Sustainability 2 (7), Peng, R., Cai, X., Xu, H., Lu, J., Wen, F., Zhang, W., Zhang, L., 2024. Lanegraph2seq:
628–634. Lane topology extraction with language model via vertex-edge encoding and
139

X. Lu and Q. Weng I S P R S J o u r n a l o f P h o t o g r a m m e t r y a n d R e m o t e S e n s i n g 2 28 (2025) 122–140
connectivity enhancement. In: Proceedings of the AAAI Conference on Artificial Xi, Y., Liu, Y., Liu, Z., Tarkoma, S., Hui, P., Li, Y., 2024. From pixels to progress:
Intelligence, pp. 4497–4505. generating road network from satellite imagery for socioeconomic insights in
Pruthi, J., Dhingra, S., 2023. A review of research on road feature extraction through impoverished areas. In: Proceedings of the Thirty-Third International Joint
remote sensing images based on deep learning algorithms. In: 2023 3rd International Conference on Artificial Intelligence, pp. 7509–7517.
Conference on Innovative Sustainable Computational Technologies (CISCT). IEEE, Xia, J., Yokoya, N., Adriano, B., Broni-Bediako, C., 2023. OpenEarthMap: a benchmark
pp. 1–5. dataset for global high-resolution land cover mapping. In: Proceedings of the IEEE/
Rasal, S., Boddhu, S.K., 2024. Beyond segmentation: Road network generation with CVF Winter Conference on Applications of Computer Vision, pp. 6254–6264.
multi-modal LLMs. Science and Information Conference. Springer 308–315. Xu, H., He, H., Zhang, Y., Ma, L., Li, J., 2023a. A comparative study of loss functions for
Ren, S., Luzi, F., Lahrichi, S., Kassaw, K., Collins, L.M., Bradbury, K., Malof, J.M., 2024. road segmentation in remotely sensed road datasets. Int. J. Appl. Earth Obs. Geoinf.
Segment anything, from space?. In: Proceedings of the IEEE/CVF Winter Conference 116, 103159.
on Applications of Computer Vision, pp. 8355–8365. Xu, J., Xu, B., Xia, G.-S., Dong, L., Xue, N., 2024. Patched line segment learning for vector
Ronneberger, O., Fischer, P., Brox, T., 2015. U-Net: Convolutional networks for road mapping. In: Proceedings of the AAAI Conference on Artificial Intelligence,
biomedical image segmentation. Medical Image Computing and Computer-Assisted pp. 6288–6296.
Intervention–MICCAI 2015: 18th International Conference, Munich, Germany, Xu, Z., Liu, Y., Gan, L., Sun, Y., Wu, X., Liu, M., Wang, L., 2022. RNGDet: Road network
October 5-9, 2015, Proceedings, part III 18. Springer, pp. 234-241. graph detection by transformer in aerial images. IEEE Trans. Geosci. Remote Sens.
Sghaier, M.O., Lepage, R., 2015. Road extraction from very high resolution remote 60, 1–12.
sensing optical images based on texture analysis and beamlet transform. IEEE J. Sel. Xu, Z., Liu, Y., Sun, Y., Liu, M., Wang, L., 2023b. RNGDet++: Road network graph
Top. Appl. Earth Obs. Remote Sens. 9 (5), 1946–1958. detection by transformer with instance segmentation and multi-scale features
Shit, S., Paetzold, J.C., Sekuboyina, A., Ezhov, I., Unger, A., Zhylka, A., Pluim, J.P., enhancement. IEEE Rob. Autom. Lett. 8 (5), 2991–2998.
Bauer, U., Menze, B.H., 2021. clDice-a novel topology-preserving loss function for Xu, Z., Sun, Y., Wang, L., Liu, M., 2021. CP-loss: Connectivity-preserving loss for road
tubular structure segmentation. In: Proceedings of the IEEE/CVF Conference on curb detection in autonomous driving with aerial images. In: 2021 IEEE/RSJ
Computer Vision and Pattern Recognition, pp. 16560–16569. International Conference on Intelligent Robots and Systems (IROS). IEEE,
Slagter, B., Fesenmyer, K., Hethcoat, M., Belair, E., Ellis, P., Kleinschroth, F., Pen˜a- pp. 1117–1123.
Claros, M., Herold, M., Reiche, J., 2024. Monitoring road development in Congo Yang, B., Zhang, M., Zhang, Z., Zhang, Z., Hu, X., 2023a. TopDiG: Class-agnostic
Basin forests with multi-sensor satellite imagery and deep learning. Remote Sens. topological directional graph extraction from remote sensing images. In: Proceedings
Environ. 315, 114380. of the IEEE/CVF Conference on Computer Vision and Pattern Recognition,
Sohn, K., Berthelot, D., Carlini, N., Zhang, Z., Zhang, H., Raffel, C.A., Cubuk, E.D., pp. 1265–1274.
Kurakin, A., Li, C.-L., 2020. FixMatch: Simplifying semi-supervised learning with Yang, R., Zhong, Y., Liu, Y., Chen, D., Pan, Y., 2024a. IS-RoadDet: Road vector graph
consistency and confidence. Adv. Neural Inf. Proces. Syst. 33, 596–608. detection with intersections and road segments from high resolution remote sensing
Sotiris, A., Lucchi, A., Hofmann, T., 2023. Mastering spatial graph prediction of road imagery. IEEE Trans. Geosci. Remote Sens. 62, 1–14.
networks. In: Proceedings of the IEEE/CVF International Conference on Computer Yang, R., Zhong, Y., Liu, Y., Lu, X., Zhang, L., 2024b. Occlusion-aware road extraction
Vision, pp. 5408–5418. network for high-resolution remote sensing imagery. IEEE Trans. Geosci. Remote
Sun, T., Di, Z., Che, P., Liu, C., Wang, Y., 2019. Leveraging crowdsourced GPS data for Sens. 62, 1–16.
road extraction from aerial imagery. In: Proceedings of the IEEE/CVF Conference on Yang, X., Li, X., Ye, Y., Lau, R.Y., Zhang, X., Huang, X., 2019. Road detection and
Computer Vision and Pattern Recognition, pp. 7509–7518. centerline extraction via deep recurrent convolutional neural network U-Net. IEEE
Tan, Y.-Q., Gao, S.-H., Li, X.-Y., Cheng, M.-M., Ren, B., 2020. VecRoad: Point-based Trans. Geosci. Remote Sens. 57 (9), 7209–7220.
iterative graph exploration for road graphs extraction. In: Proceedings of the IEEE/ Yang, Z.-X., You, Z.-H., Chen, S.-B., Tang, J., Luo, B., 2023b. Semi-supervised edge-aware
CVF Conference on Computer Vision and Pattern Recognition, pp. 8910–8918. road extraction via cross teaching between CNN and transformer. IEEE J. Sel. Top.
Tao, C., Qi, J., Li, Y., Wang, H., Li, H., 2019. Spatial information inference net: Road Appl. Earth Obs. Remote Sens. 16, 8353–8362.
extraction using road-specific contextual information. ISPRS J. Photogramm. Yin, P., Li, K., Cao, X., Yao, J., Liu, L., Bai, X., Zhou, F., Meng, D., 2024. Towards satellite
Remote Sens. 158, 155–166. image road graph extraction: A global-scale dataset and A novel method. arXiv
Tuia, D., Schindler, K., Demir, B., Camps-Valls, G., Zhu, X.X., Kochupillai, M., Dˇzeroski, preprint arXiv:2411.16733.
S., van Rijn, J.N., Hoos, H.H., Del Frate, F., 2023. Artificial intelligence to advance You, Z.-H., Wang, J.-X., Chen, S.-B., Tang, J., Luo, B., 2022. FMWDCT: Foreground mixup
Earth observation: a perspective. arXiv preprint arXiv:2305.08413. into weighted dual-network cross training for semisupervised remote sensing road
United-Nations, 2019. World population prospects 2019: Highlights. United Nations extraction. IEEE J. Sel. Top. Appl. Earth Obs. Remote Sens. 15, 5570–5579.
Department for Economic and Social Affairs. Zao, Y., Zou, Z., Shi, Z., 2023. Topology-guided road graph extraction from remote
Van Etten, A., Lindenbaum, D., Bacastow, T.M., 2018. SpaceNet: A remote sensing sensing images. IEEE Trans. Geosci. Remote Sens. 62, 1–14.
dataset and challenge series. arXiv preprint arXiv:1807.01232. Zhang, J., Hu, Q., Li, J., Ai, M., 2020. Learning from GPS trajectories of floating car for
Vargas-Munoz, J.E., Srivastava, S., Tuia, D., Falcao, A.X., 2020. OpenStreetMap: CNN-based urban road extraction with high-resolution satellite imagery. IEEE Trans.
challenges and opportunities in machine learning and remote sensing. IEEE Geosci. Geosci. Remote Sens. 59 (3), 1836–1847.
Remote Sens. Mag. 9 (1), 184–199. Zhang, L., Lan, M., Zhang, J., Tao, D., 2021. Stagewise unsupervised domain adaptation
Wang, B., Liu, Q., Hu, Z., Wang, W., Wang, Y., 2023a. TERNformer: Topology-enhanced with adversarial self-training for road segmentation of remote-sensing images. IEEE
road network extraction by exploring local connectivity. IEEE Trans. Geosci. Remote Trans. Geosci. Remote Sens. 60, 1–13.
Sens. 61, 1–14. Zhang, Z., Liu, Q., Wang, Y., 2018. Road extraction by deep residual U-Net. IEEE Geosci.
Wang, L., Dai, M., He, J., Huang, J., 2023b. Regularized primitive graph learning for Remote Sens. Lett. 15 (5), 749–753.
unified vector mapping. In: Proceedings of the IEEE/CVF International Conference Zheng, Z., Zhong, Y., Zhang, L., Burke, M., Lobell, D.B., Ermon, S., 2024. Towards
on Computer Vision, pp. 16817–16826. transferable building damage assessment via unsupervised single-temporal change
Wang, S., Bai, M., Mattyus, G., Chu, H., Luo, W., Yang, B., Liang, J., Cheverie, J., Fidler, adaptation. Remote Sens. Environ. 315, 114416.
S., Urtasun, R., 2016. TorontoCity: Seeing the world with a million eyes. arXiv Zhou, L., Zhang, C., Wu, M., 2018. D-LinkNet: LinkNet with pretrained encoder and
preprint arXiv:1612.00423. dilated convolution for high resolution satellite imagery road extraction. In:
Wang, X., Jin, X., Dai, Z., Wu, Y., Chehri, A., 2025. Deep learning-based methods for road Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition
extraction from remote sensing images: a vision, survey, and future directions. IEEE Workshops, pp. 182–186.
Geosci. Remote Sens. Mag. Zhou, M., Sui, H., Chen, S., Liu, J., Shi, W., Chen, X., 2022. Large-scale road extraction
Wang, Y., Tong, L., Luo, S., Xiao, F., Yang, J., 2024. A multi-scale and multi-direction from high-resolution remote sensing images based on a weakly-supervised structural
feature fusion network for road detection from satellite imagery. IEEE Trans. Geosci. and orientational consistency constraint network. ISPRS J. Photogramm. Remote
Remote Sens. 62, 1–18. Sens. 193, 234–251.
Wegner, J.D., Montoya-Zegarra, J.A., Schindler, K., 2013. A higher-order CRF model for Zhou, M., Sui, H., Chen, S., Wang, J., Chen, X., 2020. BT-RoadNet: a boundary and
road network extraction. In: Proceedings of the IEEE Conference on Computer Vision topologically-aware neural network for road extraction from high-resolution remote
and Pattern Recognition, pp. 1698–1705. sensing imagery. ISPRS J. Photogramm. Remote Sens. 168, 288–306.
Wei, Y., Ji, S., 2021. Scribble-based weakly supervised deep learning for road surface Zhou, Y., Weng, Q., 2024. Building up a data engine for global urban mapping. Remote
extraction from remote sensing images. IEEE Trans. Geosci. Remote Sens. 60, 1–12. Sens. Environ. 311, 114242.
Wei, Y., Zhang, K., Ji, S., 2020. Simultaneous road surface and centerline extraction from Zhu, Q., Zhang, Y., Wang, L., Zhong, Y., Guan, Q., Lu, X., Zhang, L., Li, D., 2021. A global
large-scale remote sensing images using CNN-based segmentation and tracing. IEEE context-aware and batch-independent network for road extraction from VHR
Trans. Geosci. Remote Sens. 58 (12), 8919–8931. satellite imagery. ISPRS J. Photogramm. Remote Sens. 175, 353–365.
Wu, Z., Pan, S., Chen, F., Long, G., Zhang, C., Philip, S.Y., 2020. A comprehensive survey
on graph neural networks. IEEE Trans. Neural Networks Learn. Syst. 32 (1), 4–24.
140