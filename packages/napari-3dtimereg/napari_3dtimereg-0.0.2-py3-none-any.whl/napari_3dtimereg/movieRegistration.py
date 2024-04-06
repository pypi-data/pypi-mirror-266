import napari
import tifffile
from magicgui import magicgui
from napari.utils.notifications import show_info
import itk
import random
import numpy as np
import pathlib
import os, glob
import napari_3dtimereg.Utils as ut
from qtpy.QtWidgets import QFileDialog
from napari.utils.history import get_save_history, update_save_history
from webbrowser import open_new_tab

"""
Napari - 3D Time Reg

Napari plugin to do movie registration with possible deformation. Uses elastix library.
Registration is calculated on one reference chanel and applied to the others.

author: Gaëlle Letort, CNRS/Institut Pasteur
"""

def get_filename():
    """ User selection of movie to process """
    dialog = QFileDialog(caption="Choose reference image")
    hist = get_save_history()
    dialog.setHistory(hist)
    dialog.setFileMode(QFileDialog.ExistingFile)
    dialog.setDirectory(hist[0])
    if dialog.exec_():
        filename = dialog.selectedFiles()
    if filename:
        return filename[0]
    else:
        return None

def start():
    global viewer, aligndir, imagedir
    global refimg, refchanel
    global resimg
    global imagename
    global scaleXY, scaleZ
    global colchan, dim
    refchanel = 0
    viewer = napari.current_viewer()
    viewer.title = "3dTimeReg"
    filename = get_filename()
    if filename is None:
        print("No file selected")
        return
    refimg, scaleXY, scaleZ, names = ut.open_image(filename, verbose=True)
    print(refimg.shape)
    ## test if 2d or 3d movie (several chanels assumed)
    if len(refimg.shape)==4:
        colchan = 1
        dim = 2
        scaleZ = -1
    else:
        colchan = 2
        dim = 3
    imagename, imagedir, aligndir = ut.extract_names( filename, subname="aligned" )
    update_save_history(imagedir)
    for chan in range(refimg.shape[colchan]):
        cmap = ut.colormapname(chan)
        if dim == 3:
            cview = viewer.add_image( refimg[:,:,chan,:,:], name="Movie_"+"C"+str(chan), blending="additive", colormap = cmap )
            quants = tuple( np.quantile( refimg[:,:,chan,:,:], [0.01, 0.9999]) )
        else:
            cview = viewer.add_image( refimg[:,chan,:,:], name="Movie_"+"C"+str(chan), blending="additive", colormap = cmap )
            quants = tuple( np.quantile( refimg[:,chan,:,:], [0.01, 0.9999]) )
        cview.contrast_limits = quants
        cview.gamma = 0.95
    return getChanels()

def getChanels():
    """ Choose the chanel on which to calculate the alignement """

    @magicgui(call_button="Update", 
            reference_chanel={"widget_type": "Slider", "min":0, "max": refimg.shape[2]-1}, 
            )
    def get_chanel( reference_chanel=0 , ):
        global refchanel
        global resimg
        global colchan
        viewer.window.remove_dock_widget("all")
        refchanel = reference_chanel
        for chan in range(refimg.shape[0]):
            layname = "Movie_"+"C"+str(chan)
            if chan != refchanel:
                if layname in viewer.layers:
                    viewer.layers.remove(layname)
            else:
                viewer.layers.remove(layname) ## tmp
            #    img = (refimg[:,:,chan,:,:])
            #    if layname in viewer.layers:
            #        viewer.layers.remove(layname)
            #        viewer.add_image( img, name=layname, blending="additive", colormap = "red" )
            #    else:
            #        viewer.layers[layname].colormap = "red"
        if "Do registration" not in viewer.window._dock_widgets:
            if dim == 2:
                resimg = np.copy(refimg[:,refchanel,:,:])
            else:
                resimg = np.copy(refimg[:,:,refchanel,:,:])
            resimg[0] = resimg[0] - np.min(resimg[0])
            cview = viewer.add_image( resimg, name="ResMovie", blending="additive", colormap = "red") 
            #quants = tuple( np.quantile( resimg, [0.01, 0.9999]) )
            #cview.contrast_limits = quants
            do_registration()
    
    wid = viewer.window.add_dock_widget(get_chanel, name="Choose chanel")
    return wid

def itk_to_layer(img, name, color):
    lay = layer_from_image(img)
    lay.blending = "additive"
    lay.colormap = color
    lay.name = name
    viewer.add_layer( lay )

def do_registration():
    """ use Elastix to perform registration with possible deformation """
    
    def calc_registration( time ):
        """ Calculate the registration between two consecutive frames """
        global resimg, dim
        global results_transform_parameters_aff, results_transform_parameters
        if get_paras.reference_frame.value == "first frame":
            if time == 0:
                save_images(0)
                return None
            fimage = itk.image_view_from_array((resimg[0]))
        if get_paras.reference_frame.value == "middle frame":
            halftime = int(resimg.shape[0]/2)
            if time == halftime:
                save_images(halftime)
                return None
            fimage = itk.image_view_from_array((resimg[halftime]))
        if get_paras.reference_frame.value == "previous":
            if time == 0:
                save_images(0)
                return None
            fimage = itk.image_view_from_array((resimg[time-1]))
        fimage = fimage.astype(itk.F)
        mimage = itk.image_view_from_array((resimg[time]))
        mimage = mimage.astype(itk.F)
        affimage = mimage 
        
        elastix_object = None
        results_transform_parameters_aff = None

        if get_paras.do_rigid.value == True:
            parameter_object = None
            parameter_object = itk.ParameterObject.New()
            parameter_map_rigid = parameter_object.GetDefaultParameterMap('rigid')
            parameter_map_rigid['MaximumNumberOfIterations'] = [str(get_paras.iterations.value)]
            parameter_map_rigid['MaximumStepLength'] = [str(get_paras.max_step_length.value)]
            parameter_map_rigid["NumberOfResolutions"] = [str(get_paras.resolution.value)]
            parameter_map_rigid['NumberOfSpatialSamples'] = ['10000']
            parameter_map_rigid['MaximumNumberOfSamplingAttempts'] = ['8']
            parameter_map_rigid['RequiredRatioOfValidSamples'] = ['0.05']
            parameter_map_rigid['CheckNumberOfSamples'] = ['false']
            final = int(get_paras.final_spacing.value)
            parameter_map_rigid['FinalGridSpacingInPhysicalUnits'] = [str(final)]
            parameter_map_rigid['Registration'] = ['MultiMetricMultiResolutionRegistration']
            parameter_map_rigid["AutomaticTransformInitialization"] = ['true']
            parameter_map_rigid["AutomaticTransformInitializationMethod"] = ['CenterOfGravity']
            space_one = int(get_paras.spacing_one.value)
            #gridspace = [str(space_one*10)+" "+str(space_one*10)+" "+str(int(space_one*2))]
            if dim == 3:
                gridspace = [str(space_one*1)+" "+str(space_one*4)+" "+str(int(space_one*4))]
            else:
                gridspace = [str(space_one)]
            resolution = int(get_paras.resolution.value)
            if resolution > 1:
                space_two = int(get_paras.spacing_two.value)
                #gridspace.append(str(space_two*5)+" "+str(space_two*5)+" "+str(int(space_two)))
                if dim == 3:
                    gridspace.append(str(space_two*1)+" "+str(space_two*2)+" "+str(int(space_two*2)))
                else:
                    gridspace.append(str(space_two))
            if resolution > 2:
                space_three = int(get_paras.spacing_three.value)
                #gridspace.append(str(space_three*5)+" "+str(space_three*5)+" "+str(space_three))
                if dim == 3:
                    gridspace.append(str(space_three*1)+" "+str(space_three*1)+" "+str(space_three))
                else:
                    gridspace.append(str(space_three*1))
            if resolution > 3:
                space_four = int(get_paras.spacing_four.value)
                if dim == 3:
                    gridspace.append(str(space_four*1)+" "+str(space_four*1)+" "+str(space_four))
                else:
                    gridspace.append(str(space_four*1))
            if resolution > 4:
                gridspace.append(str(int(get_paras.spacing_four.value)))
            parameter_map_rigid['GridSpacingSchedule'] = gridspace
            original_metric = parameter_map_rigid['Metric']
            parameter_object.AddParameterMap(parameter_map_rigid)
        
            elastix_object = None
            elastix_object = itk.ElastixRegistrationMethod.New(fimage, mimage)
            elastix_object.SetParameterObject(parameter_object)
            
            # Set additional options
            elastix_object.SetLogToConsole(get_paras.show_log.value==True)

            # Update filter object (required)
            elastix_object.UpdateLargestPossibleRegion()

            # Results of Registration
            affimage = elastix_object.GetOutput()
            results_transform_parameters_aff = elastix_object.GetTransformParameterObject()
            
            # Show intermediate layer
            if get_paras.show_intermediate_layer.value==True:
                resimage = affimage
                resclayer = layer_from_image(resimage)
                resclayer.blending = "additive"
                resclayer.name = "AfterAffineRegistration"
                viewer.add_layer( resclayer )
        
        # first rigid transformation
        if get_paras.do_bspline.value == True:
            parameter_object = None
            preset = "bspline"
            parameter_object = itk.ParameterObject.New()
            parameter_map = parameter_object.GetDefaultParameterMap(preset)
            parameter_map["NumberOfResolutions"] = [str(get_paras.resolution.value)]
            parameter_map["WriteIterationInfo"] = ["false"]
            parameter_map['MaximumStepLength'] = [str(get_paras.max_step_length.value)]
            parameter_map['NumberOfSpatialSamples'] = ['10000']
            parameter_map['MaximumNumberOfSamplingAttempts'] = ['10']
            parameter_map['RequiredRatioOfValidSamples'] = ['0.05']
            parameter_map['MaximumNumberOfIterations'] = [str(get_paras.iterations.value)]
            parameter_map['FinalGridSpacingInPhysicalUnits'] = [str(get_paras.final_spacing.value)]
            #final = int(get_paras.final_spacing.value)
            #parameter_map['FinalGridSpacingInPhysicalUnits'] = [str(final)+" "+str(final)+" "+str(int(final/5))]
            parameter_map['FinalBSplineInterpolationOrder'] = [str(3)]
            parameter_map['BSplineInterpolationOrder'] = [str(3)]
            parameter_map['HowToCombineTransform'] = ['Compose']
            gridspace = [str(get_paras.spacing_one.value)]
            space_one = int(get_paras.spacing_one.value)
            #gridspace = [str(space_one*5)+" "+str(space_one*5)+" "+str(int(space_one))]
            resolution = int(get_paras.resolution.value)
            if resolution > 1:
                gridspace.append(str(get_paras.spacing_two.value))
                space_two = int(get_paras.spacing_two.value)
                #gridspace.append(str(space_two*5)+" "+str(space_two*5)+" "+str(int(space_two)))
            if resolution > 2:
                gridspace.append(str(get_paras.spacing_three.value))
                space_three = int(get_paras.spacing_three.value)
                #gridspace.append(str(space_three*5)+" "+str(space_three*5)+" "+str(space_three))
            if resolution > 3:
                gridspace.append(str(get_paras.spacing_four.value))
                space_four = int(get_paras.spacing_four.value)
                #gridspace.append(str(space_four*5)+" "+str(space_four*5)+" "+str(space_four))
            if resolution > 4:
                gridspace.append(str(int(get_paras.spacing_four.value/2)))
            parameter_map['GridSpacingSchedule'] = gridspace
            parameter_object.AddParameterMap(parameter_map)
    
            # Load Elastix Image Filter Object
            elastix_object = itk.ElastixRegistrationMethod.New(fimage, affimage)
            elastix_object.SetParameterObject(parameter_object)
            elastix_object.SetLogToConsole(get_paras.show_log.value==True)

            # Update filter object (required)
            elastix_object.UpdateLargestPossibleRegion()

        # Results of Registration
        result_image = elastix_object.GetOutput()
        results_transform_parameters = elastix_object.GetTransformParameterObject()

        data = (itk.array_view_from_image(result_image))
        data[data<0] = 0
        data = np.array(data)
        #data = data - np.min(data)
        resimg[time] = data
        viewer.layers["ResMovie"].refresh()

        ut.writeTif( data, os.path.join(aligndir, imagename+"_C"+str(refchanel)+"_T"+"{:04d}".format(time)+".tif"), scaleXY, scaleZ, "uint16" )
        return 1
            

    @magicgui(call_button="Go", 
            reference_frame={"choices":["previous","first frame", "middle frame"]},
            max_step_length={"widget_type":"LiteralEvalLineEdit"}, 
            resolution={"widget_type":"LiteralEvalLineEdit"}, 
            iterations={"widget_type":"LiteralEvalLineEdit"}, 
            final_spacing={"widget_type":"LiteralEvalLineEdit"}, 
            spacing_one={"widget_type":"LiteralEvalLineEdit"}, 
            spacing_two={"widget_type":"LiteralEvalLineEdit"}, 
            spacing_three={"widget_type":"LiteralEvalLineEdit"}, 
            spacing_four={"widget_type":"LiteralEvalLineEdit"}, 
            )
    def get_paras( reference_frame = "previous",
            show_log = False,
            do_rigid = False,
            do_bspline = True,
            show_advanced_parameters = False,
            show_intermediate_layer = False,
            resolution=2,
            max_step_length = 2,
            iterations=1000,
            final_spacing=25, 
            spacing_one=4,
            spacing_two=2,
            spacing_three=1,
            spacing_four=1,
            ):
        
        global results_transform_parameters_aff, results_transform_parameters
        reslay = viewer.layers["ResMovie"]
        results_transform_para_aff = None
        
        for t in range(reslay.data.shape[0]):
            time = t 
            print("Calculate registration for time point "+str(time))
            done = calc_registration(time)
            if done is not None:
                apply_alignement(time)

        finish_image()


    
    def show_advanced(booly):
        get_paras.show_intermediate_layer.visible = booly
        get_paras.resolution.visible = booly
        get_paras.max_step_length.visible = booly
        get_paras.iterations.visible = booly
        get_paras.final_spacing.visible = booly
        get_paras.spacing_one.visible = booly
        get_paras.spacing_two.visible = booly
        get_paras.spacing_three.visible = booly
        get_paras.spacing_four.visible = booly

    show_advanced(False)
    get_paras.show_advanced_parameters.changed.connect(show_advanced)
    wid = viewer.window.add_dock_widget(get_paras, name="Calculate alignement")
    return wid

def layer_from_image(img):
    data = np.array(itk.array_view_from_image(img))
    image_layer = napari.layers.Image(data)
    return image_layer

def save_images(time):
    """ Save all chanels unmoved of frame time """
    global dim
    if dim == 3:
        chanellist = list(range(refimg.shape[2]))
    else:
        chanellist = list(range(refimg.shape[1]))
    for chan in chanellist:
        if dim == 3:
            res = np.copy(refimg[time,:,chan,:,:])
            #res = res - np.min(res)
            res = np.uint16(res)
            ut.writeTif( res, os.path.join(aligndir, imagename+"_C"+str(chan)+"_T"+"{:04d}".format(time)+".tif"), scaleXY, scaleZ, "uint16" )
        else:
            res = np.copy(refimg[time,chan,:,:])
            #res = res - np.min(res)
            res = np.uint16(res)
            ut.writeTif( res, os.path.join(aligndir, imagename+"_C"+str(chan)+"_T"+"{:04d}".format(time)+".tif"), scaleXY, -1, "uint16" )

def apply_alignement(time):
    """ Apply caclulated registration to the other chanels """
    global dim
    global results_transform_parameters_aff, results_transform_parameters
    if dim == 2:
        chanellist = list(range(refimg.shape[1]))
    else:
        chanellist = list(range(refimg.shape[2]))
    align_chanels = []
    for chan in chanellist:
        if chan != refchanel:
            align_chanels.append(chan)

    print("Apply alignment to "+str(align_chanels))
    for chan in align_chanels:
        if dim == 2:
            img = refimg[time,chan,:,:]
        else:
            img = refimg[time,:,chan,:,:]
        res = []
        itkimage = itk.image_view_from_array(img)
        itkimage = itkimage.astype(itk.F)
        ImageType = itk.Image[itk.F, dim]
        if results_transform_parameters_aff is not None:
            transformix_filter = itk.TransformixFilter[ImageType].New()
            transformix_filter.SetMovingImage(itkimage)
            transformix_filter.SetTransformParameterObject(results_transform_parameters_aff)
            aff_image = transformix_filter.GetOutput()
        else:
            aff_image = itkimage
        
        if results_transform_parameters is not None:
            transformix = itk.TransformixFilter[ImageType].New()
            transformix.SetMovingImage(aff_image)
            transformix.SetTransformParameterObject(results_transform_parameters)
            res_image = transformix.GetOutput()
        else:
            res_image = aff_image

        res = itk.array_from_image(res_image)
        res[res<0] = 0
        res = np.array(res)
        #res = res - np.min(res)
        res = np.uint16(res)
        
        ut.writeTif( res, os.path.join(aligndir, imagename+"_C"+str(chan)+"_T"+"{:04d}".format(time)+".tif"), scaleXY, scaleZ, "uint16" )

def finish_image():
    """ End, create composite image """
    global movimg
    remove_widget("Calculate alignement")
    remove_layer("ResMovie")
    create_result_image()

def remove_layer(layname):
    if layname in viewer.layers:
        viewer.layers.remove(layname)

def remove_widget(widname):
    if widname in viewer.window._dock_widgets:
        wid = viewer.window._dock_widgets[widname]
        wid.setDisabled(True)
        del viewer.window._dock_widgets[widname]
        wid.destroyOnClose()

def create_result_image():
    """ Create one final composite movies of aligned images """
    
    @magicgui(call_button = "Concatenate aligned images",)
    def get_files():
        resimg = np.zeros(refimg.shape) 
        if dim == 2:
            nchans = refimg.shape[1]
        else:
            nchans = refimg.shape[2]

        for chan in range(nchans):
            for time in range(refimg.shape[0]):
                filename = os.path.join(aligndir, imagename+"_C"+str(chan)+"_T"+"{:04d}".format(time)+".tif")
                img, tscaleXY, tscaleZ, names = ut.open_image(filename, verbose=False)
                resimg[time, chan, :,:] = img
                os.remove(filename)

        viewer.add_image(resimg, name="Res", blending="additive")
        for lay in viewer.layers:
            if lay.name != "Res":
                remove_layer(lay)
        imgname = os.path.join(aligndir, imagename+".tif")
        resimg = np.array(resimg, "uint16")
        # move the chanel axis after the Z axis (imageJ format)
        if dim == 3:
            resimg = np.moveaxis(resimg, 0, 1)
        tifffile.imwrite(imgname, resimg, imagej=True, resolution=[1./scaleXY, 1./scaleXY], metadata={'PhysicalSizeX': scaleXY, 'spacing': scaleZ, 'unit': 'um', 'axes': 'ZCYX'})
        show_info("Image "+imgname+" saved")
    
    viewer.window.add_dock_widget(get_files, name="Concatenate")
