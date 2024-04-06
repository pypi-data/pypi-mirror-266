import numpy as np
import os

def colormapname( i ):
    colorsmaps = ["red", "green", "blue", "yellow", "cyan", "gray"]
    return colorsmaps[i]

def openims(imagepath, verbose=True):
    """ Open ims image """
    from imaris_ims_file_reader.ims import ims
    img = ims(imagepath, squeeze_output=True)
    image = np.array(img[0])
    scaleXY = img.resolution[1]
    if img.resolution[2] != scaleXY:
        print("Warning, scale is not the same in X and Y, not implemented yet")
    scaleZ = img.resolution[0]
    if verbose:
        print("Initial image shape: "+str(image.shape))    ## Y et X sont inverses, Z, Y, X
    nchan = img.Channels
    names = []
    try:
        if nchan > 0:
            for i in range(nchan):
                name = img.read_attribute("DataSetInfo/Channel "+str(i), 'DyeName')
                names.append(name)
    except:
        names = []
    img = None

    return (np.squeeze(image), scaleXY, scaleZ, names)

def writeims(imagepath, img, verbose=True):
    ## libraries pb, must install hdf5, ImarisWriter
    from PyImarisWriter import PyImarisWriter as pw
    imshape = img.shape
    image_size = pw.ImageSize(x=imshape[2], y=imshape[1], z=imshape[0], c=1, t=1)
    dimension_sequence = pw.DimensionSequence('z', 'y', 'x', 'c', 't')
    block_size = image_size
    sample_size = pw.ImageSize(x=1, y=1, z=1, c=1, t=1)
    output_filename = 'outifle.ims'

    options = pw.Options()
    options.mNumberOfThreads = 12
    options.mCompressionAlgorithmType = pw.eCompressionAlgorithmGzipLevel2
    options.mEnableLogProgress = True

    application_name = 'PyImarisWriter'
    application_version = '1.0.0'

    #callback_class = MyCallbackClass()
    converter = pw.ImageConverter("uint8", image_size, sample_size, dimension_sequence, block_size,
                                  output_filename, options, application_name, application_version, None)

    num_blocks = image_size / block_size

    block_index = pw.ImageSize()
    for c in range(num_blocks.c):
        block_index.c = c
        for t in range(num_blocks.t):
            block_index.t = t
            for z in range(num_blocks.z):
                block_index.z = z
                for y in range(num_blocks.y):
                    block_index.y = y
                    for x in range(num_blocks.x):
                        block_index.x = x
                        if converter.NeedCopyBlock(block_index):
                            converter.CopyBlock(img, block_index)

    adjust_color_range = True
    image_extents = pw.ImageExtents(0, 0, 0, image_size.x, image_size.y, image_size.z)
    parameters = pw.Parameters()
    parameters.set_value('Image', 'ImageSizeInMB', 2400)
    parameters.set_value('Image', 'Info', 'Results Title')
    parameters.set_channel_name(0, 'My Channel 1')
    time_infos = [datetime.today()]
    color_infos = [pw.ColorInfo() for _ in range(image_size.c)]
    color_infos[0].set_color_table(configuration.mColor_table)

    converter.Finish(image_extents, parameters, time_infos, color_infos, adjust_color_range)

    converter.Destroy()
    print('Wrote file')

def writeTif(img, imgname, scaleXY, scaleZ, imtype):
    import tifffile
    ### 2D
    if scaleZ < 0:
        tifffile.imwrite(imgname, np.array(img, dtype=imtype), imagej=True, resolution=[1./scaleXY, 1./scaleXY], metadata={'unit': 'um', 'axes': 'YX'})
    #### 3D
    else:
        tifffile.imwrite(imgname, np.array(img, dtype=imtype), imagej=True, resolution=[1./scaleXY, 1./scaleXY], metadata={'spacing': scaleZ, 'unit': 'um', 'axes': 'ZYX'})

def get_scale_of(racine, c):
    """ read scaling value from xml metadata """
    try:
        part = racine.xpath("//Distance [@Id = '%s']" % c)
        for neighbor in part[0].iter('Value'):
            pixel_in_meters = float(neighbor.text)
    except:
        pixel_in_meters = -1
    return pixel_in_meters*1000000

def openczi(imagepath, scene=0, verbose=True):
    """ Open czi image """
    import czifile
    from lxml import etree
    czi = czifile.CziFile(imagepath)
    image = czi.asarray()
    if verbose:
        print("Initial image shape: "+str(image.shape))

    if image.ndim >= 8:
        image = image[:,scene,:,:,:,:,:,:]  ## si contient 2 scenes

    # get scale
    root = etree.fromstring(czi.metadata())
    scaleXY = get_scale_of(root, "X")
    scaleXYcheck = get_scale_of(root, "Y")
    if scaleXY != scaleXYcheck:
        print("Warning, scale not the same in X and in Y, not implemented yet")
    scaleZ = get_scale_of(root, "Z")

    fluonames = get_fluo_names(root)
    return (np.squeeze(image), scaleXY, scaleZ, fluonames)

def get_filename():
    try:
        from tkinter import Tk
        from tkFileDialog import askopenfilenames
    except:
        from tkinter import Tk
        from tkinter import filedialog

    Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
    filenames = filedialog.askopenfilenames() # show an "Open" dialog box and return the path to the selected file
    return filenames

def opentif(imagepath, verbose=True):
    import tifffile as tif
    img = tif.TiffFile(imagepath)
    metadata = img.imagej_metadata
    names = []
    scaleXY = 1
    scaleZ = 1
    try:
        if metadata is not None:
            info = img.imagej_metadata["Info"]
            for i in range(10):
                ind = info.find("channels_channel_"+str(i)+"_dyename")
                if ind >= 0:
                    keep = info[ind:]
                    indend = keep.find("\n")
                    names.append(info[ind+28:ind+indend].strip())
     
            metadata = (img.imagej_metadata['Info']).splitlines()
            scaleXY = float(metadata[-4].split()[2])*1000000
            scaleZ = float(metadata[-2].split()[2])*1000000
    except:
        scaleXY = 0.25
        scaleZ = 1
    image = img.asarray()
    img.close()
    return image, scaleXY, scaleZ, names

def arrange_dims(image, verbose=True):
    ## test if there is a chanel dimension. If yes, put it first in the order
    if len(image.shape)>3:
        chanpos = np.where(image.shape==np.min(image.shape))[0][0]
        if chanpos != 0:
            image = image.swapaxes(chanpos, 0)

    ## if there is no chanel dimension, add one to always have one
    if image.shape[0]>5:
        image = np.expand_dims(image, axis=0)

    if verbose:
        print("Image dimensions: "+str(image.shape))

        return image

def extract_names(imagepath, subname="results"):
    imgname = os.path.splitext(os.path.basename(imagepath))[0]
    imgdir = os.path.dirname(imagepath)
    resdir = os.path.join(imgdir, subname)
    if not os.path.exists(resdir):
        os.makedirs(resdir)
    return imgname, imgdir, resdir

def open_image(imagepath, verbose=True):
    imagename = os.path.splitext(os.path.basename(imagepath))[0]
    ext = os.path.splitext(imagepath)[1]
    if ext == ".ims":
        return openims(imagepath, verbose)
    elif ext == ".czi":
        return openczi(imagepath, verbose)
    elif (ext == ".tif") or (ext == ".tiff"):
        return opentif(imagepath, verbose)
    else: 
        print("Image format not implemented yet")

def select_slices(image, bestz, scaleZ, zmargin=10, rm_empty=True, verbose=True):
    """ Keep only slices around bestz and slices that contain signal """
    
    dz = int(zmargin/scaleZ)    ## keep 10 microns under and above reference z
    limLz = max(bestz-int(dz),0)  
    limHz = min(bestz+dz, (image[0,:,0,0].size))
    if verbose:
        print("Z limits "+str(limLz)+" "+str(limHz))

    ## Remove slices with nearly nothing
    if rm_empty:
        simage = np.sum(image, axis=0)
        zsimage = np.sum(simage, axis=1)
        zsimage = np.sum(zsimage, axis=1)
        empty = zsimage<np.mean(zsimage)-1*np.std(zsimage)
        while empty[limLz] and limLz<limHz:
            limLz += 1
        while empty[limHz-1] and limHz>limLz:
            limHz = limHz - 1

    if verbose:
        print("Final Z limits "+str(limLz)+" "+str(limHz))

    image = image[:,limLz:limHz,:,:]
    bestz = bestz-limLz
    if verbose:
        print('Global reference z: '+str(bestz))
    return image, bestz

