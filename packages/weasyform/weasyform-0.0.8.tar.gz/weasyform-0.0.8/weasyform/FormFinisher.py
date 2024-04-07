import datetime
import pydyf
import weasyprint


class FormFinisher:
    def __init__(self, inject_empty_cryptographic_signature: bool = False, is_signature_visible: bool = False):
        self.inject_empty_cryptographic_signature = inject_empty_cryptographic_signature
        self.is_signature_visible = is_signature_visible

    def _find_form_field(self, pdf: pydyf.PDF, input_name: str) -> pydyf.Dictionary:
        def _filter_conditions(pdf_o: pydyf.Object) -> bool:
            # Has to be pydyf.Dictionary
            if not isinstance(pdf_o, pydyf.Dictionary):
                return False

            # has to be Type == /Annot
            if pdf_o.get('Type') != '/Annot':
                return False

            # has to be Subtype == /Widget
            if pdf_o.get('Subtype') != '/Widget':
                return False

            # has to have T and it has to be of type pydyf.String
            t = pdf_o.get('T')
            if not t or not isinstance(t, pydyf.String):
                return False

            if isinstance(t.string, pydyf.String):
                # There is a ?bug? in weasyprint where input name is packed twice in pydyf.String
                name = t.string.string
            else:
                name = t.string

            # T has to be same value as input we want to remove
            if input_name != name:
                return False

            return True

        for pdf_object in pdf.objects:
            if _filter_conditions(pdf_object):
                return pdf_object

    def _append_empty_cryptographic_signature(self, pdf: pydyf.PDF) -> pydyf.Dictionary:
        signature_max_length = 16384 * 2
        date = datetime.datetime.utcnow()
        date = date.strftime('%Y%m%d%H%M%S+00\'00\'')
        form_signature = pydyf.Dictionary({
            'Type': '/Sig',
            'Filter': '/Adobe.PPKLite',
            'SubFilter': '/ETSI.CAdES.detached',
            'ByteRange[0 ********** ********** **********]': '/M(D:{date})'.format(date=date),
            #'Contents<{zeros}>'.format(zeros='0' * signature_max_length): ''
        })

        pdf.add_object(form_signature)

        return form_signature

    def _ensure_sig_flags(self, pdf: pydyf.PDF):
        acro_form = pdf.catalog.get('AcroForm')

        if not acro_form.get('SigFlags'):
            acro_form.update(pydyf.Dictionary({
                'SigFlags': 1
            }))

    def _create_visible_signature_box(self, pdf: pydyf.PDF, signature_field: pydyf.Dictionary, display: bool = True):
        llx, lly, urx, ury = signature_field['Rect']
        w = abs(urx - llx)
        h = abs(ury - lly)
        if w and h:
            ap_dict = pydyf.Dictionary()
            if display:
                ap_stream = pydyf.Stream([], {
                    'BBox': pydyf.Array([0, h, w, 0]),
                    'Resources': pydyf.Dictionary(),
                    'Type': '/XObject',
                    'Subtype': '/Form',
                })
                ap_stream.push_state()

                # Background
                ap_stream.push_state()
                ap_stream.set_color_rgb('0.95', '0.95', '0.95')
                ap_stream.rectangle(0, 0, w, h)
                ap_stream.fill()
                ap_stream.pop_state()

                # Border
                ap_stream.set_line_width('0.5')
                ap_stream.rectangle(0, 0, w, h)
                ap_stream.stroke()
                ap_stream.pop_state()

            else:
                ap_stream = pydyf.Stream([], {
                    'BBox': pydyf.Array([0, h, w, 0]),
                    'Resources': pydyf.Dictionary(),
                    'Type': '/XObject',
                    'Subtype': '/Form',
                })

            pdf.add_object(ap_stream)
            ap_dict['N'] = ap_stream.reference

            signature_field['AP'] = ap_dict

    def override_field(self, pdf: pydyf.PDF, input_name: str):
        found_element = self._find_form_field(pdf, input_name)
        if not found_element:
            raise ValueError('Input with name {} not found'.format(input_name))
        found_element['FT'] = '/Sig'
        found_element['F'] = 132,
        found_element['T'] = pydyf.String(input_name)  #!FIXME we have to override name since weasyprint doublepacks T in pydyf.String -> pydyf.String
        if self.inject_empty_cryptographic_signature:
            found_element['V'] = self._append_empty_cryptographic_signature(pdf).reference
        else:
            del found_element['V']  # Remove V (value) since it is set to pydyf.String and that may break signing in some pdf readers???
        del found_element['DA']  # Remove DA whoever it is lol

        if found_element.get('Rect'):
            self._create_visible_signature_box(pdf, found_element, self.is_signature_visible)

        """
        This is how field created by weasyprint looks like
         field = pydyf.Dictionary({
                'Type': '/Annot',  OK
                'Subtype': '/Widget', OK
                'Rect': pydyf.Array(rectangle), OK?
                'FT': '/Tx',  CHANGE
                'F': 1 << (3 - 1),  # Print flag  132
                'P': page.reference, OK
                'T': pydyf.String(input_name),
                'V': pydyf.String(value or ''),
                'DA': pydyf.String(b' '.join(field_stream.stream)),
            })
        """
        """
        This is how it should look like
        data = {
            'FT': '/Sig',
            'T': pydyf.String(field_name),
            'Type': '/Annot',
            'Subtype': '/Widget',
            'F': annotation_flag,
            'Rect': rect,
        }
        """

    def __call__(self, pdf_document: weasyprint.Document, pdf: pydyf.PDF):
        found_signature_field = False
        for page_number, page in enumerate(pdf_document.pages):
            for element, style, rectangle in page.inputs:
                if element.attrib.get('type') == 'signature':
                    input_name = element.attrib.get('name')
                    self.override_field(pdf, input_name)
                    found_signature_field = True

        if found_signature_field:
            self._ensure_sig_flags(pdf)
