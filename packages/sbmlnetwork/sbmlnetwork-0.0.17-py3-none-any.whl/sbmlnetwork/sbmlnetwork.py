import libsbmlnetwork as sbmln
import networkinfotranslator as netranslator
from PIL import Image
from IPython.core.display import display

class SBMLNetwork:

    """
    A wrapper class to use libSBMLNetwork, which is an API to work with the Layout and Render packages of libSBML

    """
    def __init__(self, sbml):

        """
        Initializes the SBMLNetwork class by reading an SBML document from the given file name or the given text string

        :Parameters:

            - sbml: an SBML document in the form of either an SBML string or an SBML file (.xml) directory
        """

        self.sbml_object = None
        self.load(sbml)

    def load(self, sbml):

        """
        Reads an SBML document from the given file name or the given text string

        :Parameters:

            - sbml (string): a string that determines either the name or full pathname of the SBML(.xml) file to be read
                or a string containing a full SBML model.

        :Returns:

            SBMLDocument: a pointer to the SBMLDocument structure created from the SBML content in the given file name or
                from the SBML content in the given text string
        """

        self.sbml_object = sbmln.readSBML(sbml)
        return self.sbml_object

    def export(self, file_name=""):
        """
        Writes the given SBML document to either the file_name or a string

        :Parameters:

            - file_name (string, optional): a string (default : "") that determines the name or full pathname of the file where the SBML is to be written

        :Returns:

            either success: true on success and false if the filename could not be opened for writing
            or text: the SBML text string on success and empty string if one of the underlying parser components fail.
        """

        if file_name:
            return sbmln.writeSBML(self.sbml_object, file_name)
        else:
            return sbmln.writeSBML(self.sbml_object)

    def autolayout(self, stiffness=10.0, gravity=15.0, use_magnetism=False, use_boundary=False, use_grid=False):
        """
        checks if a Layout object, a GlobalRenderInformation object, and LocalRenderInformation object does not exists in the SBMLDocument,
            then adds them to it, and set all the necessary features for them.

        :Parameters:

            - stiffness (float, optional): a float (default: 10.0) that determines the stiffness value used in the autolayout algorithm (can affect the canvas dimensions).
            - gravity (float, optional): a float (default: 15.0) that determines the gravity value used in the autolayout algorithm (can affect the how densely nodes are distributed).
            - use_magnetism (boolean, optional): a boolean (default: False) that determines whether to use magnetism in the autolayout algorithm.
            - useBoundary (boolean, optional): a boolean (default: False) that determines whether to use boundary restriction in the autolayout algorithm.
            - use_grid (boolean, optional): a boolean (default: False) that determines whether to use grid restriction in the autolayout algorithm.

        :Returns:

            either success: true on success and false if the filename could not be opened for writing
            or text: the SBML text string on success and empty string if one of the underlying parser components fail.
        """

        return sbmln.autolayout(self.sbml_object, stiffness, gravity, use_magnetism, use_boundary, use_grid)

    def draw(self, file_directory="", file_name="", file_format="", display_image=True):
        """
        create an image of the network using networkinfotranslator package, save it as file to the provided directory (or the current directory), and then load and display it

        :Parameters:

            - file_directory (string, optional): a string (default: "") that specifies the directory to which the output image will be saved.
            - file_name (string, optional): a string (default: "") that specifies the name of the output image.
            - file_format (string, optional): a sting (default: "") that specifies that format of the output image (examples are 'pdf', 'png', 'svg', and 'jpg')
            - display_image (boolean, optional): a boolean (default: True) that determines whether to display the generated image or not

        """
        if not self._layout_is_specified() or not self._render_is_specified():
            self.autolayout()

        sbml_graph_info = netranslator.NetworkInfoImportFromSBMLModel()
        sbml_graph_info.extract_info(self.export())
        sbml_export = netranslator.NetworkInfoExportToMatPlotLib()
        sbml_export.extract_graph_info(sbml_graph_info)
        sbml_export.export(file_directory, file_name, file_format)
        if display_image and file_format != "pdf":
            display(Image.open(sbml_export.get_output_name(file_directory, file_name, file_format)))

    def _layout_is_specified(self):
        if sbmln.getNumLayouts(self.sbml_object):
            return True

        return False

    def _render_is_specified(self):
        if sbmln.getNumGlobalRenderInformation(self.sbml_object) or sbmlne.getNumLocalRenderInformation(self.sbml_object):
            return True

        return False
