from matplotlib.pyplot import axis
from utils.plot import plot17j_2d
import torch
import numpy as np
from torch.utils.data import Dataset
import pickle
import copy
from utils.skeleton import Skeleton
from utils.mocap_dataset import MocapDataset
from utils.camera import normalize_screen_coordinates, image_coordinates

class H36MDataset(Dataset):
    """Human3.6M dataset including images."""

    def __init__(self, poses_3d, poses_2d, confidences,subjects, normalize_2d=True):
        # pickle_off = open(fname, "rb")
        # self.data = pickle.load(pickle_off)
        self.poses_2d=poses_2d
        self.poses_3d=poses_3d
        self.subjects=subjects
        self.conf=confidences

        # # select subjects
        # selection_array = np.zeros(len(self.data['subjects']), dtype=bool)
        # for s in subjects:
        #     selection_array = np.logical_or(selection_array, (np.array(self.data['subjects']) == s))

        # self.data['subjects'] = list(np.array(self.data['subjects'])[selection_array])
        # cams = ['54138969', '55011271', '58860488', '60457274']
        # for cam in range(len(poses_2d)):
            # self.poses[cam] = self.data['poses_2d_pred'][cam][selection_array]
            # self.data['confidences'][cam] = self.data['confidences'][cam][selection_array]
            # print(self.data['poses_2d_pred'][cam].shape)
            # x=self.data['poses_2d_pred'][cam][100:101,[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]]
            # y=self.data['poses_2d_pred'][cam][100:101,[16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31]]
            # pos2d=np.concatenate((np.expand_dims(x,axis=2),np.expand_dims(y,axis=2)),axis=2)
            # plot17j_2d(pos2d.reshape(1,16,2))
            # if normalize_2d:
            #     self.poses_2d[cam] = (self.poses_2d[cam].reshape(-1, 2, 16) -
            #                                   self.poses_2d[cam].reshape(-1, 2, 16)[:, :, [6]]).reshape(-1, 32)
            #     self.data['poses_2d_pred'][cam] /= np.linalg.norm(self.poses_2d[cam], ord=2, axis=1, keepdims=True)

    def __len__(self):
        return self.poses_2d[0].shape[0]

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        sample = dict()

        # cams = ['54138969', '55011271', '58860488', '60457274']
        pad=13
        # if idx-pad>0 and self.poses_2d[0].shape[0]>=pad+idx+1:

        for c_idx in range(len(self.poses_2d)):
            p2d = torch.Tensor(self.poses_2d[c_idx][idx].astype('float32')).cuda()
            p3d = torch.Tensor(self.poses_3d[c_idx][idx].astype('float32')).cuda()

            sample['cam' + str(c_idx)] = p2d
            sample['cam' + str(c_idx)+'_3d'] = p3d
        # else:

        #     for c_idx in range(len(self.poses_2d)):
        #         p2d = torch.zeros_like(torch.Tensor(self.poses_2d[c_idx][100:127])).cuda()
        #         sample['cam' + str(c_idx)] = p2d


        sample['confidences'] = dict()
        for c_idx in range(len(self.poses_2d)):
            if self.conf is None:
                sample['confidences'][c_idx] = torch.ones(15) #torch.Tensor(self.data['confidences'][cam][idx].astype('float32')).cuda() #
            else:
                sample['confidences'][c_idx] = torch.Tensor(self.conf[c_idx][idx].astype('float32')).cuda()
        sample['subjects'] = self.subjects[idx]

        return sample


class H36MDataset_test(Dataset):
    """Human3.6M dataset including images."""

    def __init__(self, pose_2d, confidences, pose_3d):
        self.pose_2d=pose_2d
        self.pose_3d=pose_3d
        self.conf=confidences


    def __len__(self):
        return self.pose_2d.shape[0]

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        sample = dict()
        
        # pad=13
        # if idx-pad>0 and self.pose_2d.shape[0]>=pad+idx+1:
        # 
        #     sample['poses_2d']=torch.Tensor(self.pose_2d[idx-pad:idx+pad+1].astype('float32')).cuda()
        # else:
        #     sample['poses_2d']=torch.zeros_like(torch.Tensor(self.pose_2d[100:127])).cuda()
        sample['poses_2d']=torch.Tensor(self.pose_2d[idx].astype('float32')).cuda()
        sample['poses_3d']=torch.Tensor(self.pose_3d[idx].astype('float32')).cuda()
        if self.conf is None:
            sample['confidences']=torch.ones(15)
        else:
            sample['confidences']=torch.Tensor(self.conf[idx].astype('float32')).cuda()
  
        return sample

# Copyright (c) 2018-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

#[4, 5, 9, 10, 11, 16, 20, 21, 22, 23, 24, 28, 29, 30, 31]
h36m_skeleton = Skeleton(parents=[-1,  0,  1,  2,  3,  4,  0,  6,  7,  8,  9,  0, 11, 12, 13, 14, 12,
       16, 17, 18, 19, 20, 19, 22, 12, 24, 25, 26, 27, 28, 27, 30],
       joints_left=[6, 7, 8, 9, 10, 16, 17, 18, 19, 20, 21, 22, 23],
       joints_right=[1, 2, 3, 4, 5, 24, 25, 26, 27, 28, 29, 30, 31])
# h36m_skeleton = Skeleton(parents=[-1,  0,  1, 2,  0,  4,  5, 8, 7, 8, 9,
#        10, 11, 12, 13, 14, 15],
#        joints_left=[4, 5, 6, 11, 12, 13],
#        joints_right=[1, 2, 3, 14, 15, 16])

h36m_cameras_intrinsic_params = [
    {
        'id': '54138969',
        'center': [512.54150390625, 515.4514770507812],
        'focal_length': [1145.0494384765625, 1143.7811279296875],
        'radial_distortion': [-0.20709891617298126, 0.24777518212795258, -0.0030751503072679043],
        'tangential_distortion': [-0.0009756988729350269, -0.00142447161488235],
        'res_w': 1000,
        'res_h': 1002,
        'azimuth': 70, # Only used for visualization
    },
    {
        'id': '55011271',
        'center': [508.8486328125, 508.0649108886719],
        'focal_length': [1149.6756591796875, 1147.5916748046875],
        'radial_distortion': [-0.1942136287689209, 0.2404085397720337, 0.006819975562393665],
        'tangential_distortion': [-0.0016190266469493508, -0.0027408944442868233],
        'res_w': 1000,
        'res_h': 1000,
        'azimuth': -70, # Only used for visualization
    },
    {
        'id': '58860488',
        'center': [519.8158569335938, 501.40264892578125],
        'focal_length': [1149.1407470703125, 1148.7989501953125],
        'radial_distortion': [-0.2083381861448288, 0.25548800826072693, -0.0024604974314570427],
        'tangential_distortion': [0.0014843869721516967, -0.0007599993259645998],
        'res_w': 1000,
        'res_h': 1000,
        'azimuth': 110, # Only used for visualization
    },
    {
        'id': '60457274',
        'center': [514.9682006835938, 501.88201904296875],
        'focal_length': [1145.5113525390625, 1144.77392578125],
        'radial_distortion': [-0.198384091258049, 0.21832367777824402, -0.008947807364165783],
        'tangential_distortion': [-0.0005872055771760643, -0.0018133620033040643],
        'res_w': 1000,
        'res_h': 1002,
        'azimuth': -110, # Only used for visualization
    },
]

h36m_cameras_extrinsic_params = {
    'S1': [
        {
            'orientation': [0.1407056450843811, -0.1500701755285263, -0.755240797996521, 0.6223280429840088],
            'translation': [1841.1070556640625, 4955.28466796875, 1563.4454345703125],
            'R': [[-0.9153617321513369, 0.40180836633680234, 0.02574754463350265], [0.051548117060134555, 0.1803735689384521, -0.9822464900705729], [-0.399319034032262, -0.8977836111057917, -0.185819527201491]], 
            't': [-346.05078140028075, 546.9807793144001, 5474.481087434061],
        },
        {
            'orientation': [0.6157187819480896, -0.764836311340332, -0.14833825826644897, 0.11794740706682205],
            'translation': [1761.278564453125, -5078.0068359375, 1606.2650146484375],
            'R': [[0.9281683400814921, 0.3721538354721445, 0.002248380248018696], [0.08166409428175585, -0.1977722953267526, -0.976840363061605], [-0.3630902204349604, 0.9068559102440475, -0.21395758897485287]],
            't': [251.42516271750836, 420.9422103702068, 5588.195881837821], 
        },
        {
            'orientation': [0.14651472866535187, -0.14647851884365082, 0.7653023600578308, -0.6094175577163696],
            'translation': [-1846.7777099609375, 5215.04638671875, 1491.972412109375],
            'R': [[-0.9141549520542256, -0.40277802228118775, -0.045722952682337906], [-0.04562341383935874, 0.21430849526487267, -0.9756999400261069], [0.4027893093720077, -0.889854894701693, -0.214287280609606]],
            't': [480.482559565337, 253.83237471361554, 5704.207679370455],
        },
        {
            'orientation': [0.5834008455276489, -0.7853162288665771, 0.14548823237419128, -0.14749594032764435],
            'translation': [-1794.7896728515625, -3722.698974609375, 1574.8927001953125],
            'R': [[0.9141562410494211, -0.40060705854636447, 0.061905989962380774], [-0.05641000739510571, -0.2769531972942539, -0.9592261660183036], [0.40141783470104664, 0.8733904688919611, -0.2757767409202658]], 
            't': [51.88347637559197, 378.4208425426766, 4406.149140878431],
        },
    ],
    'S2': [
        {},
        {},
        {},
        {},
    ],
    'S3': [
        {},
        {},
        {},
        {},
    ],
    'S4': [
        {},
        {},
        {},
        {},
    ],
    'S5': [
        {
            'orientation': [0.1467377245426178, -0.162370964884758, -0.7551892995834351, 0.6178938746452332],
            'translation': [2097.3916015625, 4880.94482421875, 1605.732421875],
            'R': [[-0.9042074184788829, 0.42657831374650107, 0.020973473936051274], [0.06390493744399675, 0.18368565260974637, -0.9809055713959477], [-0.4222855708380685, -0.8856017859436166, -0.1933503902128034]], 
            't': [-219.3059666108619, 544.4787497640639, 5518.740477016156],
        },
        {
            'orientation': [0.6159758567810059, -0.7626792192459106, -0.15728192031383514, 0.1189815029501915],
            'translation': [2031.7008056640625, -5167.93310546875, 1612.923095703125],
            'R': [[0.9222116004775194, 0.38649075753002626, 0.012274293810989732], [0.09333184463870337, -0.19167233853095322, -0.9770111982052265], [-0.3752531555110883, 0.902156643264318, -0.21283434941998647]],
            't': [103.90282067751986, 395.67169468951965, 5767.97265758172],
        },
        {
            'orientation': [0.14291371405124664, -0.12907841801643372, 0.7678384780883789, -0.6110143065452576],
            'translation': [-1620.5948486328125, 5171.65869140625, 1496.43701171875],
            'R': [[-0.9258288614330635, -0.3728674116124112, -0.06173178026768599], [-0.023578112500148365, 0.220000562347259, -0.9752147584905696], [0.3772068291381898, -0.9014264506460582, -0.21247437993123308]], 
            't': [520.3272318446208, 283.3690958234795, 5591.123958858676],
        },
        {
            'orientation': [0.5920479893684387, -0.7814217805862427, 0.1274748593568802, -0.15036417543888092],
            'translation': [-1637.1737060546875, -3867.3173828125, 1547.033203125],
            'R': [[0.9222815489764817, -0.3772688722588351, 0.0840532119677073], [-0.021177649402562934, -0.26645871124348197, -0.9636136478735888], [0.3859381447632816, 0.88694303832152, -0.25373962085111357]], 
            't': [-79.116431351199, 425.59047114848386, 4454.481629705836],
        },
    ],
    'S6': [
        {
            'orientation': [0.1337897777557373, -0.15692396461963654, -0.7571090459823608, 0.6198879480361938],
            'translation': [1935.4517822265625, 4950.24560546875, 1618.0838623046875],
            'R': [[-0.9149503344107554, 0.4034864343564006, 0.008036345687245266], [0.07174776353922047, 0.1822275975157708, -0.9806351824867137], [-0.3971374371533952, -0.896655898321083, -0.19567845056940925]], 
            't': [-239.5182864132218, 545.8141831785044, 5523.931578633363],
        },
        {
            'orientation': [0.6147197484970093, -0.7628812789916992, -0.16174767911434174, 0.11819244921207428],
            'translation': [1969.803955078125, -5128.73876953125, 1632.77880859375],
            'R': [[0.9197364689900042, 0.39209901596964664, 0.018525368698999664], [0.101478073351267, -0.19191459963948, -0.9761511087296542], [-0.37919260045353465, 0.899681692667386, -0.21630030892357308]], 
            't': [169.02510061389722, 409.6671223380997, 5714.338002825065],
        },
        {
            'orientation': [0.1529948115348816, -0.13529130816459656, 0.7646096348762512, -0.6112781167030334],
            'translation': [-1769.596435546875, 5185.361328125, 1476.993408203125],
            'R': [[-0.916577698818659, -0.39393483656788014, -0.06856140726771254], [-0.01984531630322392, 0.21607069980297702, -0.9761760169700323], [0.3993638509543854, -0.8933805444629346, -0.20586334624209834]],
            't': [521.9864793089763, 286.28272817103516, 5643.2724406159],
        },
        {
            'orientation': [0.5916101336479187, -0.7804774045944214, 0.12832270562648773, -0.1561593860387802],
            'translation': [-1721.668701171875, -3884.13134765625, 1540.4879150390625],
            'R': [[0.9182950552949388, -0.3850769011116475, 0.09192372735651859], [-0.015534985886560007, -0.26706146429979655, -0.9635542737695438], [0.3955917790277871, 0.8833990913037544, -0.25122338635033875]], 't': [-56.29675276801464, 420.29579722027506, 4499.322693551688], 'R': [[0.9182950552949388, -0.3850769011116475, 0.09192372735651859], [-0.015534985886560007, -0.26706146429979655, -0.9635542737695438], [0.3955917790277871, 0.8833990913037544, -0.25122338635033875]],
            't': [-56.29675276801464, 420.29579722027506, 4499.322693551688], 
        },
    ],
    'S7': [
        {
            'orientation': [0.1435241848230362, -0.1631336808204651, -0.7548328638076782, 0.6188824772834778],
            'translation': [1974.512939453125, 4926.3544921875, 1597.8326416015625],
            'R': [[-0.9055764231419416, 0.42392653746206904, 0.014752378956221508], [0.06862812683752326, 0.18074371881263407, -0.9811329615890764], [-0.41859469903024304, -0.8874784498483331, -0.19277053457045695]], 
            't': [-323.9118424584857, 541.7715234126381, 5506.569132699328],
        },
        {
            'orientation': [0.6141672730445862, -0.7638262510299683, -0.1596645563840866, 0.1177929937839508],
            'translation': [1937.0584716796875, -5119.7900390625, 1631.5665283203125],
            'R': [[0.9212640765077017, 0.3886011826562522, 0.01617473877914905], [0.09922277503271489, -0.1946115441987536, -0.9758489574618522], [-0.3760682680727248, 0.9006194910741931, -0.21784671226815075]], 
            't': [178.6238708832376, 403.59193467821774, 5694.8801003668095],
        },
        {
            'orientation': [0.14550060033798218, -0.12874816358089447, 0.7660516500473022, -0.6127139329910278],
            'translation': [-1741.8111572265625, 5208.24951171875, 1464.8245849609375],
            'R': [[-0.9245069728829368, -0.37555597339631824, -0.06515034871105972], [-0.018955014220249346, 0.2160111098950734, -0.9762068980691586], [0.38069353097569036, -0.9012751584550871, -0.2068224461344045]], 
            't': [441.1064712697594, 271.9161436257393, 5660.120611352617],
        },
        {
            'orientation': [0.5912848114967346, -0.7821764349937439, 0.12445473670959473, -0.15196487307548523],
            'translation': [-1734.7105712890625, -3832.42138671875, 1548.5830078125],
            'R': [[0.9228353966173104, -0.37440015452287667, 0.09055029013436408], [-0.01498208436370467, -0.269786590656035, -0.9628035794752281], [0.38490306298896904, 0.8871525910436372, -0.25457791009093983]], 
            't': [25.76853374383657, 431.05581759025813, 4461.872981411145],
        },
    ],
    'S8': [
        {
            'orientation': [0.14110587537288666, -0.15589867532253265, -0.7561917304992676, 0.619644045829773],
            'translation': [2150.65185546875, 4896.1611328125, 1611.9046630859375],
            'R': [[-0.9115694669712032, 0.4106494283805017, 0.020202818036194434], [0.060907749548984036, 0.1834736632003901, -0.9811359034082424], [-0.40660958293025334, -0.8931430243150293, -0.19226072190306673]], 
            't': [-82.70216069652597, 552.1896311377282, 5557.353609418419], 
        },
        {
            'orientation': [0.6169601678848267, -0.7647668123245239, -0.14846350252628326, 0.11158157885074615],
            'translation': [2219.965576171875, -5148.453125, 1613.0440673828125],
            'R': [[0.931016282525616, 0.3647626932499711, 0.01252434769597448], [0.08939715221301257, -0.19463753190599434, -0.9767929055586687], [-0.35385990285476776, 0.9105297407479727, -0.2138194574051759]],
            't': [-209.06289992510443, 375.0691429434037, 5818.276676972416], 
        },
        {
            'orientation': [0.1471444070339203, -0.13377119600772858, 0.7670128345489502, -0.6100369691848755],
            'translation': [-1571.2215576171875, 5137.0185546875, 1498.1761474609375],
            'R': [[-0.9209075762929309, -0.3847355178017309, -0.0625125368875214], [-0.02568138180824641, 0.21992027027623712, -0.9751797482259595], [0.38893405939143305, -0.8964450100611084, -0.21240678280563546]], 
            't': [623.0985110132146, 290.9053651845054, 5534.379001592981], 
        },
        {
            'orientation': [0.5927824378013611, -0.7825870513916016, 0.12147816270589828, -0.14631995558738708],
            'translation': [-1476.913330078125, -3896.7412109375, 1547.97216796875],
            'R': [[0.927667052235436, -0.3636062759574404, 0.08499597802942535], [-0.01666268768012713, -0.26770413351564454, -0.9633570738505596], [0.37303645269074087, 0.8922583555131325, -0.2543989622245125]], 
            't': [-178.36705625795474, 423.4669232560848, 4421.6448791590965], 
        },
    ],
    'S9': [
        {
            'orientation': [0.15540587902069092, -0.15548215806484222, -0.7532095313072205, 0.6199594736099243],
            'translation': [2044.45849609375, 4935.1171875, 1481.2275390625],
            'R': [[-0.9033486204435297, 0.4269119782787646, 0.04132109321984796], [0.04153061098352977, 0.182951140059007, -0.9822444139329296], [-0.4268916470184284, -0.8855930460167476, -0.18299857527497945]], 
            't': [-321.2078335720134, 467.13452033013084, 5514.330338522134], 
        },
        {
            'orientation': [0.618784487247467, -0.7634735107421875, -0.14132238924503326, 0.11933968216180801],
            'translation': [1990.959716796875, -5123.810546875, 1568.8048095703125],
            'R': [[-0.9269344193869241, -0.3732303525241731, -0.03862235247246717], [-0.04725991098820678, 0.218240494552814, -0.9747500127472326], [0.37223525218497616, -0.901704048173249, -0.21993345934341726]],
            't': [455.40107288876885, 273.3589338272866, 5657.814488280711], 
        },
        {
            'orientation': [0.13357827067375183, -0.1367100477218628, 0.7689454555511475, -0.6100738644599915],
            'translation': [-1670.9921875, 5211.98583984375, 1528.387939453125],
            'R': [[-0.9269344193869241, -0.3732303525241731, -0.03862235247246717], [-0.04725991098820678, 0.218240494552814, -0.9747500127472326], [0.37223525218497616, -0.901704048173249, -0.21993345934341726]],
            't': [455.40107288876885, 273.3589338272866, 5657.814488280711], 
        },
        {
            'orientation': [0.5879399180412292, -0.7823407053947449, 0.1427614390850067, -0.14794869720935822],
            'translation': [-1696.04345703125, -3827.099853515625, 1591.4127197265625],
            'R': [[0.9154607080837831, -0.39734606500700814, 0.06362229623477154], [-0.049406284684695274, -0.2678916756611978, -0.9621814117644814], [0.3993628813352506, 0.877695935238897, -0.26487569589663096]], 
            't': [-69.27125529438378, 422.18433660888445, 4457.893374979774],
        },
    ],
    'S11': [
        {
            'orientation': [0.15232472121715546, -0.15442320704460144, -0.7547563314437866, 0.6191070079803467],
            'translation': [2098.440185546875, 4926.5546875, 1500.278564453125],
            'R': [[-0.9059013006181885, 0.4217144115102914, 0.038727105014486805], [0.044493184429779696, 0.1857199061874203, -0.9815948619389944], [-0.4211450938543295, -0.8875049698848251, -0.1870073216538954]], 
            't': [-234.7208032216618, 464.34018262882194, 5536.652631113797],
        },
        {
            'orientation': [0.6189449429512024, -0.7600917220115662, -0.15300633013248444, 0.1255258321762085],
            'translation': [2083.182373046875, -4912.1728515625, 1561.07861328125],
            'R': [[0.9216646531492915, 0.3879848687925067, -0.0014172943441045224], [0.07721054863099915, -0.18699239961454955, -0.979322405373477], [-0.3802272982247548, 0.9024974149959955, -0.20230080971229314]], 
            't': [-11.934348472090557, 449.4165893644565, 5541.113551868937],
        },
        {
            'orientation': [0.14943228662014008, -0.15650227665901184, 0.7681233882904053, -0.6026304364204407],
            'translation': [-1609.8153076171875, 5177.3359375, 1537.896728515625],
            'R': [[-0.9063540572469627, -0.42053101768163204, -0.04093880896680188], [-0.0603212197838846, 0.22468715090881142, -0.9725620980997899], [0.4181909532208387, -0.8790161246439863, -0.2290130547809762]], 
            't': [781.127357651581, 235.3131620173424, 5576.37044019807],
        },
        {
            'orientation': [0.5894251465797424, -0.7818877100944519, 0.13991211354732513, -0.14715361595153809],
            'translation': [-1590.738037109375, -3854.1689453125, 1578.017578125],
            'R': [[0.91754082476548, -0.39226322025776267, 0.06517975852741943], [-0.04531905395586976, -0.26600517028098103, -0.9629057236990188], [0.395050652748768, 0.8805514269006645, -0.2618476013752581]],
            't': [-155.13650339749012, 422.16256306729633, 4435.416222660868],
        },
    ],
}

class Human36mDataset(MocapDataset):
    def __init__(self, path, remove_static_joints=True):
        super().__init__(fps=50, skeleton=h36m_skeleton)
        
        self._cameras = copy.deepcopy(h36m_cameras_extrinsic_params)
        for cameras in self._cameras.values():
            for i, cam in enumerate(cameras):
                cam.update(h36m_cameras_intrinsic_params[i])
                for k, v in cam.items():
                    if k not in ['id', 'res_w', 'res_h']:
                        cam[k] = np.array(v, dtype='float32')
                
                # Normalize camera frame
                cam['center'] = normalize_screen_coordinates(cam['center'], w=cam['res_w'], h=cam['res_h']).astype('float32')
                cam['focal_length'] = cam['focal_length']/cam['res_w']*2
                if 'translation' in cam:
                    cam['translation'] = cam['translation']/1000 # mm to meters
                if 't' in cam:
                    cam['t'] = cam['t']/1000 # mm to meters
                
                # Add intrinsic parameters vector
                cam['intrinsic'] = np.concatenate((cam['focal_length'],
                                                   cam['center'],
                                                   cam['radial_distortion'],
                                                   cam['tangential_distortion']))        
        
        # Load serialized dataset
        data = np.load(path, allow_pickle=True)['positions_3d'].item()
        
        self._data = {}
        for subject, actions in data.items():
            self._data[subject] = {}
            for action_name, positions in actions.items():
                self._data[subject][action_name] = {
                    'positions': positions,
                    'cameras': self._cameras[subject],
                }
                
        if remove_static_joints:
            # Bring the skeleton to 17 joints instead of the original 32
            self.remove_joints([4, 5, 9, 10, 11, 16, 20, 21, 22, 23, 24, 28, 29, 30, 31])
            
            # Rewire shoulders to the correct parents
            self._skeleton._parents[11] = 8
            self._skeleton._parents[14] = 8
            
    def supports_semi_supervised(self):
        return True
   