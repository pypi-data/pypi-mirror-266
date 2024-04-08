import pathlib
import unittest
import asyncio
from functools import partial
from unittest.mock import patch, AsyncMock
from pprint import pprint


from patent_chart import parser
from patent_chart import generator
from patent_chart import utils
from patent_chart import filtering
from patent_chart import ranking

# NOTE: relic of when we were trying to parse the whole patent from the pdf.
# class TestParser(unittest.TestCase):
#     package_dir = pathlib.Path(__file__).parents[1]
#     patent_257_path = package_dir / 'test_data/US 6,484,257.pdf'
#     patent_131_path = package_dir / 'test_data/US 7,600,131.pdf'
#     patent_479_path = package_dir / 'test_data/US 5,870,479.pdf'
#     patent_448_path = package_dir / 'test_data/US7069448.pdf'
#     patent_449_path = package_dir / 'test_data/7069449.pdf'
#     patent_application_path = package_dir / 'test_data/US20210365512A1.pdf'
#     patent_325_path = package_dir / 'test_data/US7031325.pdf'
    
#     def test_parse_patent_from_pdf_path(self):
#         text_lines = parser.parse_text_lines_from_pdf_path(self.patent_257_path)
#         parsed_patent = parser.parse_patent_from_text_lines(text_lines)
#         # print(parser.group_parsed_patent_by_page(parsed_patent)[23].column_1)
#         # return
#         self.assertEqual(
#             parsed_patent.unique_id,
#             parser.PatentUniqueID(
#                 patent_number='6484257',
#                 country_code='US',
#                 kind_code='B1',
#             )
#         )
#         self.assertEqual(
#             parsed_patent.beginning_of_specification,
#             16
#         )
#         # claims = parser.parse_claims_from_parsed_patent(parsed_patent)
#         # for claim in claims.claims:
#         #     print(parser.serialize_claim(claim))
#         # return
#         # pprint(claims)
#         self.assertEqual(
#             parsed_patent.beginning_of_claims,
#             parser.BeginningOfClaims(
#                 page_index=23,
#                 col_index=0,
#                 line_index=16,
#             )
#         )
#         self.assertEqual(
#             parsed_patent.end_of_claims,
#             parser.EndOfClaims(
#                 page_index=23,
#                 col_index=1,
#                 line_index=74,
#             )
#         )

#         text_lines = parser.parse_text_lines_from_pdf_path(self.patent_131_path)
#         parsed_patent = parser.parse_patent_from_text_lines(text_lines)
#         self.assertEqual(
#             parsed_patent.unique_id,
#             parser.PatentUniqueID(
#                 patent_number='7600131',
#                 country_code='US',
#                 kind_code='B1',
#             )
#         )
#         self.assertEqual(
#             parsed_patent.beginning_of_specification,
#             12
#         )
#         self.assertEqual(
#             parsed_patent.beginning_of_claims,
#             parser.BeginningOfClaims(
#                 page_index=22,
#                 col_index=0,
#                 line_index=11,
#             )
#         )
#         self.assertEqual(
#             parsed_patent.end_of_claims,
#             parser.EndOfClaims(
#                 page_index=22,
#                 col_index=1,
#                 line_index=42,
#             )
#         )

#         text_lines = parser.parse_text_lines_from_pdf_path(self.patent_479_path)
#         parsed_patent = parser.parse_patent_from_text_lines(text_lines)
#         self.assertEqual(
#             parsed_patent.unique_id,
#             parser.PatentUniqueID(
#                 patent_number='5870479',
#                 country_code='US',
#                 kind_code='A',
#             )
#         )
#         self.assertEqual(
#             parsed_patent.beginning_of_specification,
#             4
#         )
#         self.assertEqual(
#             parsed_patent.beginning_of_claims,
#             parser.BeginningOfClaims(
#                 page_index=7,
#                 col_index=0,
#                 line_index=8,
#             )
#         )
#         self.assertEqual(
#             parsed_patent.end_of_claims,
#             parser.EndOfClaims(
#                 page_index=7,
#                 col_index=1,
#                 line_index=50,
#             )
#         )

#         text_lines = parser.parse_text_lines_from_pdf_path(self.patent_application_path)
#         parsed_patent = parser.parse_patent_from_text_lines(text_lines)
#         self.assertEqual(
#             parsed_patent.unique_id,
#             parser.PatentUniqueID(
#                 patent_number='20210365512',
#                 country_code='US',
#                 kind_code='A1',
#             )
#         )

#         self.assertEqual(
#             parsed_patent.beginning_of_specification,
#             15
#         )

#         # # TODO: doesn't work yet searching for specific prefatory language because there is none in this case. Would have to have some model to catch this one. Could count number of 'X.' bigrams on page, could use simple naive bayes model, could even just ask LLM.
#         # self.assertEqual(
#         #     parsed_patent.beginning_of_claims,
#         #     parser.BeginningOfClaims(
#         #         page_index=22,
#         #         col_index=0,
#         #         line_index=0,
#         #     )
#         # )
#         # # TODO: doesn't work for this one either
#         # self.assertEqual(
#         #     parsed_patent.end_of_claims,
#         #     parser.EndOfClaims(
#         #         page_index=24,
#         #         col_index=1,
#         #         line_index=0,
#         #     )
#         # )

#         parsed_patent = parser.parse_patent_from_pdf_path(self.patent_448_path)
#         self.assertEqual(
#             parsed_patent.unique_id,
#             parser.PatentUniqueID(
#                 patent_number='7069448',
#                 country_code='US',
#                 kind_code='B2',
#             )
#         )
#         self.assertEqual(
#             parsed_patent.beginning_of_specification,
#             4
#         )
#         self.assertEqual(
#             parsed_patent.beginning_of_claims,
#             parser.BeginningOfClaims(
#                 page_index=6,
#                 col_index=1,
#                 line_index=25,
#             )
#         )
#         self.assertEqual(
#             parsed_patent.end_of_claims,
#             parser.EndOfClaims(
#                 page_index=7,
#                 col_index=1,
#                 line_index=23,
#             )
#         )

#         # TODO: doesnt work because each page of 449 is a figure. None of the text is selectable. Each page contains a pdfminer.six LTFigure object, which might be an embedded pdf. see comment in pdfminer.six/pdfminer/layout.py: class LTFigure(LTLayoutContainer):
#         """Represents an area used by PDF Form objects.

#         PDF Forms can be used to present figures or pictures by embedding yet
#         another PDF document within a page. Note that LTFigure objects can appear
#         recursively.
#         """
#         # So we might just need to recurse through LTFigure objects when we encounter them as the page contents.
#         # parsed_patent = parser.parse_patent_from_pdf_path(self.patent_449_path)

#         # TODO: test specific expected lines

#     def test_parse_some_more_patents(self):
#         parsed_patent = parser.parse_patent_from_pdf_path(self.patent_325_path)
#         self.assertEqual(
#             parsed_patent.unique_id,
#             parser.PatentUniqueID(
#                 patent_number='7031325',
#                 country_code='US',
#                 kind_code='B1',
#             )
#         )
#         self.assertEqual(
#             parsed_patent.beginning_of_specification,
#             8
#         )

#         self.assertEqual(
#             parsed_patent.beginning_of_claims,
#             parser.BeginningOfClaims(
#                 page_index=13,
#                 col_index=1,
#                 line_index=50,
#             )
#         )
        
#         self.assertEqual(
#             parsed_patent.end_of_claims,
#             parser.EndOfClaims(
#                 page_index=15,
#                 col_index=1,
#                 line_index=43,
#             )
#         )

#     # def test_parse_broad_set_us_patents(self):
#     #     us_patents_dir = self.package_dir / 'us_patents_1980-2020'
#     #     path_to_expected = {
#     #         'US6727522.pdf': {
#     #             'unique_id': parser.PatentUniqueID(
#     #                 patent_number='6727522',
#     #                 country_code='US',
#     #                 kind_code='B2',
#     #             ),
#     #             'beginning_of_specification': 10,
#     #             'beginning_of_claims': parser.BeginningOfClaims(
#     #                 page_index=6,
#     #                 col_index=1,
#     #                 line_index=25,
#     #             ),
#     #             'end_of_claims': parser.EndOfClaims(
#     #                 page_index=7,
#     #                 col_index=1,
#     #                 line_index=23,
#     #             ),
#     #             'randomly_selected_claim_element': (
#     #                 ()
#     #             )
#     #         },
#     #     }
        
#     #     for pdf_path in us_patents_dir.glob('*.pdf'):
#     #         print(pdf_path.name)
#     #         if pdf_path.name == 'USRE48787.pdf':
#     #             continue
#     #         # if pdf_path.name == 'US6727522.pdf':
#     #         #     continue
#     #         # parsed_patent = parser.parse_patent_from_pdf_path(pdf_path)
#     #         # print(parsed_patent.unique_id)

#     #         # claims = parser.parse_claims_from_parsed_patent(parsed_patent)
#     #         unique_id = parser.parse_patent_unique_id_from_pdf_path(pdf_path)
#     #         print(unique_id)

#     def test_parse_claims_from_parsed_patent(self):
#         parsed_patent = parser.parse_patent_from_pdf_path(self.patent_257_path)
#         claims = parser.parse_claims_from_parsed_patent(parsed_patent)
#         first_claim = parser.serialize_claim(claims.claims[0])
#         self.assertEqual(
#             first_claim,
#             "1. A software architecture for conducting a plurality of 15cryptographic sessions over a distributed computingenvironment, comprising:a registration entity or registry residing within a mamserver entity;an agent server entity communicating with said mam 20server;a client entity communicating with said main server andagent server;a plurality of distributed networked computers providinga mechanism for executing said main server entity,agent server entity, and client entity;a defined protocol for initiating secure communicationbetween the main server and agent server; over saidnetwork; anda system for providing one or more communicationsessions among the main server, agent server and cliententity for implementing a client decrypted bandwidthreconstitution which enables the recombination of individual parts of the decrypted client bandwidth among Nagents processing in parallel."
#         )

#         claim_elements = parser.serialize_claim_elements(claims.claims[0])
#         # TODO: see 'over said network;' parsed as it's own element. Apparently can't rely on ';' separating claim elements in every case.
#         self.assertEqual(
#             claim_elements,
#             ['1. A software architecture for conducting a plurality of 15cryptographic sessions over a distributed computingenvironment, comprising:', 'a registration entity or registry residing within a mamserver entity;', 'an agent server entity communicating with said mam 20server;', 'a client entity communicating with said main server andagent server;', 'a plurality of distributed networked computers providinga mechanism for executing said main server entity,agent server entity, and client entity;', 'a defined protocol for initiating secure communicationbetween the main server and agent server;', 'over saidnetwork;', 'anda system for providing one or more communicationsessions among the main server, agent server and cliententity for implementing a client decrypted bandwidthreconstitution which enables the recombination of individual parts of the decrypted client bandwidth among Nagents processing in parallel.']
#         )

#         parsed_patent = parser.parse_patent_from_pdf_path(self.patent_448_path)
#         claims = parser.parse_claims_from_parsed_patent(parsed_patent)
        
#         serialized_claim_1 = parser.serialize_claim_elements(claims.claims[0])
#         self.assertEqual(
#             serialized_claim_1,
#             ['1. A system for cryptographic processing of input data ona parallel processor array that includes a plurality of processors, comprising:', 'a format filter adapted to extract control data and maindata from the input data;', 'a control unit adapted to receive the control data from saidformat filter, and to forward, based at least in part on thecontrol data, at least one respective control parameterand at least one respective cryptographic parameter toeach of the plurality of processors;', 'a first distributor adapted to receive the main data fromsaid format filter, and to distribute to each of theplurality of processors a respective at least a portion ofthe main data;', 'a second distributor adapted to receive respective outputinformation from each of the plurality of processors,and to generate, based at least in part on the respectiveoutput information, output data;', 'wherein each of the plurality of processors is adapted togenerate its respective output information based at leastin part on the control parameters and the cryptographicparameters, and the output data is a cryptographicprocessing result.']
#         )

#         parsed_patent = parser.parse_patent_from_pdf_path(self.patent_479_path)
#         claims = parser.parse_claims_from_parsed_patent(parsed_patent)
#         claim_elements = parser.serialize_claim_elements(claims.claims[-1])
#         self.assertEqual(
#             claim_elements,
#             # TODO: need to fix these floating line number lines that get tacked on (3016 should be 16)
#             ['3016. A device for cryptographically processing datapackets, each of the data packets belonging to at least one ofa plurality of channels, the device comprising:', 'identification means for identifying the at least one channel to which a data packet belongs;', 'processing means for cryptographically processing thedata packet, wherein the processing means include afirst processing unit and a second processing unit;', 'memory means for storing information, associated witheach of the plurality of channels, for processing datapackets from each of the plurality a channels;', 'andcontrol means for selecting information associated withthe at least one channel which the data packet wasidentified as belonging to, wherein the control meansare designed to assign, on the basis of the identificationof the data packet, the data packet to one of the first andsecond processing units and to process the data packetwith the aid of the selected information.']
#         )

#     def test_serialize_specification_from_parsed_patent(self):
#         parsed_patent = parser.parse_patent_from_pdf_path(self.patent_257_path)
#         specification = parser.serialize_specification_from_parsed_patent(parsed_patent)

#         self.assertEqual(
#             specification[:13],
#             ['1', 'SYSTEM AND METHOD FOR MAINTAINING', 'N NUMBER OF SIMULTANEOUS', 'CRYPTOGRAPHIC SESSIONS USING A', 'DISTRIBUTED COMPUTING', 'ENVIRONMENT', 'FIELD OF THE INVENTION', 'The field of the present invention relates generally to the', 'encryption and decryption of data conducted over a distrib', 'uted computer network. In particular, the field of the inven', 'tion relates to a software architecture for conducting a', 'plurality of cryptographic sessions managed over a distrib', 'uted computing environment.']
#         )

#         parsed_patent = parser.parse_patent_from_pdf_path(self.patent_131_path)
#         specification = parser.serialize_specification_from_parsed_patent(parsed_patent)
#         self.assertEqual(
#             specification[-1],
#             'claims and their full scope of equivalents.'
#         )


class TestParseGooglePatents(unittest.TestCase):
    package_dir = pathlib.Path(__file__).parents[1]

    def test_parse_broad_set_us_patents_google(self):
        n_parse_failures = 0
        n_parse_claims_failures = 0
        us_patents_dir = self.package_dir / 'us_patents_1980-2020'
        for pdf_path in us_patents_dir.glob('*.pdf'):
            parsed_google_patent = parser.parse_google_patent_from_pdf_path(pdf_path)
            if parsed_google_patent is None:
                print(f'Failed to parse {pdf_path}')
                n_parse_failures += 1
            else:
                claims = parser.parse_claims_from_google_parsed_patent(parsed_google_patent)
                if claims is None:
                    print(f'Failed to parse claims from {pdf_path}')
                    n_parse_claims_failures += 1

        self.assertEqual(n_parse_failures, 0)
        self.assertEqual(n_parse_claims_failures, 0)


class TestFiltering(unittest.TestCase):
    def test_filtering(self):
        generated_passages = [
            generator.GeneratedPassage(
                claim_element_id=0,
                prior_art_source_id=1,
                text='generated passage',
                model_id='model',
            ),
            generator.GeneratedPassage(
                claim_element_id=0,
                prior_art_source_id=2,
                text='another generated passage',
                model_id='model',
            ),
        ]
        serialized_prior_art_source = 'generated passage'
        filter_pipeline = [partial(filtering.inclusion, super_string=serialized_prior_art_source), partial(filtering.min_length, min_length=5)]

        filter_mask = filtering.get_filter_mask([p.text for p in generated_passages], *filter_pipeline)
        self.assertEqual(len(filter_mask), 2)
        self.assertEqual(
            filter_mask,
            [True, False]
        )

        filtered_passages = filtering.apply_filter_pipeline([p.text for p in generated_passages], *filter_pipeline)
        self.assertEqual(len(filtered_passages), 1)
        self.assertEqual(
            filtered_passages,
            ['generated passage']
        )


class TestAsyncGenerator(unittest.IsolatedAsyncioTestCase):
    package_dir = pathlib.Path(__file__).parents[1]
    patent_448_path = package_dir / 'test_data/US7069448.pdf'
    patent_131_path = package_dir / 'test_data/US 7,600,131.pdf'
    patent_257_path = package_dir / 'test_data/US 6,484,257.pdf'

    @patch('patent_chart.generator.aopenai_chat_completion_request_with_retry', new_callable=AsyncMock)
    async def test_async_generate(self, mock_aopenai_chat_completion_request_with_retry):
        """
        Does not test parsing of openai output. Generated passages will typically be multiple passages separated by newlines rather than just a single passage 'generated_passage'
        """
        mock_aopenai_chat_completion_request_with_retry.return_value = ({
            'choices': [
                {
                    'message': {
                        'content': 'generated_passage'
                    },
                }
            ]
        })
        parsed_patent_448 = parser.parse_google_patent_from_pdf_path(self.patent_448_path)
        parsed_patent_131 = parser.parse_google_patent_from_pdf_path(self.patent_131_path)
        parsed_patent_257 = parser.parse_google_patent_from_pdf_path(self.patent_257_path)

        claims_448 = parsed_patent_448.claims
        
        serialized_claim_elements = []
        for claim in claims_448:
            serialized_claim_elements.extend(claim.claim_elements)

        generated_passages = set()
        full_generated_passages = []
        async for generated_passage in generator.abulk_generate_passages(
            (1, parsed_patent_448),
            [(1, parsed_patent_131), (2, parsed_patent_257)],
            [(i, serialized_claim_elements[i]) for i in range(len(serialized_claim_elements))],
            {'ranking_model_version': 'text-embedding-3-large'}
        ):
            generated_passages.add(
                (generated_passage.claim_element_id, generated_passage.prior_art_source_id)
            )
            full_generated_passages.append(generated_passage)
        
        self.assertEqual(
            len(generated_passages),
            2 * len(serialized_claim_elements)
        )

        self.assertEqual(
            generated_passages,
            set(
                [
                    (j, i) for i in range(1, 3) for j in range(len(serialized_claim_elements))
                ]
            )
        )

    def test_parse_gpt4_responses(self):
        """
        These passages were extracted from patent 131
        """
        case1 = "\"Many methods to perform cryptography are well known in\nthe art and are discussed, for example, in Applied Cryptogra\nphy, Bruce Schneier, John Wiley & Sons, Inc. (1996, rd\nEdition), herein incorporated by reference. In order to\nimprove the speed of cryptography processing, specialized\ncryptography accelerator chips have been developed.\"\n\n\"Moreover, the architecture of prior art chips does not allow\nfor the processing of cryptographic data at rates sustainable\nby the network infrastructure in connection with which these\nchips are generally implemented. This can result in noticeable 60\ndelays when cryptographic functions are invoked, for\nexample, in e-commerce transactions.\"\n\n\"In one aspect, the present invention provides a cryptogra-\nphy acceleration chip. The chip includes a plurality of cryp\ntography processing engines, and a packet distributor unit.\""

        parsed_case1 = generator.post_process_selected_passage_gpt4(case1)

        self.assertEqual(
            parsed_case1,
            [
                'Many methods to perform cryptography are well known in\nthe art and are discussed, for example, in Applied Cryptogra\nphy, Bruce Schneier, John Wiley & Sons, Inc. (1996, rd\nEdition), herein incorporated by reference. In order to\nimprove the speed of cryptography processing, specialized\ncryptography accelerator chips have been developed.',
                'Moreover, the architecture of prior art chips does not allow\nfor the processing of cryptographic data at rates sustainable\nby the network infrastructure in connection with which these\nchips are generally implemented. This can result in noticeable 60\ndelays when cryptographic functions are invoked, for\nexample, in e-commerce transactions.',
                'In one aspect, the present invention provides a cryptogra-\nphy acceleration chip. The chip includes a plurality of cryp\ntography processing engines, and a packet distributor unit.'
            ]
        )

        case2 = "\"Full support for IPSec Security Association Database lookup, including wildcard rules, overlapping rules, and complete ordering of database entries.\"\n\"Because of the pipelined design, throughput is gated by the slowest set of stages.\"\n\"The micro-engine is started by an event-driven mechanism.\""

        parsed_case2 = generator.post_process_selected_passage_gpt4(case2)

        self.assertEqual(
            parsed_case2,
            [
                'Full support for IPSec Security Association Database lookup, including wildcard rules, overlapping rules, and complete ordering of database entries.',
                'Because of the pipelined design, throughput is gated by the slowest set of stages.',
                'The micro-engine is started by an event-driven mechanism.'
            ]
        )

        case3 = "1. \"For every new packet, the distributor com\npletes the sequential portions of IPSec processing, and\nassigns the packet to the next free engine. Once the engine\ncompletes processing the packet, the processed packet is\nplaced in a retirement buffer.\"\n\n2. \"The distributor unit with an order maintenance packet\nretirement unit.\"\n\n3. \"The packet distributor unit 306 then distributes the security\nassociation information (SA) received from the packet classifier\namong a plurality of cryptography processing engines 316, on the chip 200, for security processing.\""

        parsed_case3 = generator.post_process_selected_passage_gpt4(case3)

        self.assertEqual(
            parsed_case3,
            [
                'For every new packet, the distributor com\npletes the sequential portions of IPSec processing, and\nassigns the packet to the next free engine. Once the engine\ncompletes processing the packet, the processed packet is\nplaced in a retirement buffer.',
                'The distributor unit with an order maintenance packet\nretirement unit.',
                'The packet distributor unit 306 then distributes the security\nassociation information (SA) received from the packet classifier\namong a plurality of cryptography processing engines 316, on the chip 200, for security processing.'
            ]
        )

        case4 = "\"When an outbound packet is received by the packet classifier on a cryptography acceleration chip in accordance with the present invention, its header is parsed ( 652) and a SPD lookup is performed (654).\"\n\n\"Once in the system, a SAD lookup is conducted (660).\"\n\n\"The input to ACE consists of packet classification fields: src/dst address, src/dst ports, and protocol. The output of ACE is an IPSec Security Association matching entry, if one exists, for this classification information within the IPSec Security Association Database.\""

        parsed_case4 = generator.post_process_selected_passage_gpt4(case4)

        self.assertEqual(
            parsed_case4,
            [
                'When an outbound packet is received by the packet classifier on a cryptography acceleration chip in accordance with the present invention, its header is parsed ( 652) and a SPD lookup is performed (654).',
                'Once in the system, a SAD lookup is conducted (660).',
                'The input to ACE consists of packet classification fields: src/dst address, src/dst ports, and protocol. The output of ACE is an IPSec Security Association matching entry, if one exists, for this classification information within the IPSec Security Association Database.'
            ]
        )

    # NOTE: relic of when we were trying to parse the whole patent from the pdf.
    # def test_cite_passages(self):
    #     test_passages = [
    #         'Many methods to perform cryptography are well known in\nthe art and are discussed, for example, in Applied Cryptogra\nphy, Bruce Schneier, John Wiley & Sons, Inc. (1996, rd\nEdition), herein incorporated by reference. In order to\nimprove the speed of cryptography processing, specialized\ncryptography accelerator chips have been developed.',
    #         'Moreover, the architecture of prior art chips does not allow\nfor the processing of cryptographic data at rates sustainable\nby the network infrastructure in connection with which these\nchips are generally implemented. This can result in noticeable 60\ndelays when cryptographic functions are invoked, for\nexample, in e-commerce transactions.',
    #         'In one aspect, the present invention provides a cryptogra-\nphy acceleration chip. The chip includes a plurality of cryp\ntography processing engines, and a packet distributor unit.'
    #     ]

    #     test_passages_with_newlines_removed = [
    #         'Many methods to perform cryptography are well known in the art and are discussed, for example, in Applied Cryptogra phy, Bruce Schneier, John Wiley & Sons, Inc. (1996, rd Edition), herein incorporated by reference. In order to improve the speed of cryptography processing, specialized cryptography accelerator chips have been developed.',
    #         'The packet distributor unit is configured to receive data packets and matching classification information for the packets;',
    #         'The method involves receiving data packets on a cryptography acceleration chip, processing the data packets and matching classification information for the packets,',
    #         'Most functions of the distributor are performed via dedicated hardware assist logic as opposed to microcode, since the distributor 206 is directly in the critical path of per-packet processing.',
    #         'When an outbound packet is received by the packet classifier on a cryptography acceleration chip in accordance with the present invention, its header is parsed ( 652) and a SPD lookup is performed (654).',
    #         'Distributor Microcode Overview In one implementation of the present invention, the distributor unit has a micro-engine large register file (128 entries by 32-bits), good microcode RAM size (128 entries by 96-bits), and a simple three stage pipeline design that is visible to the instruction set via register read delay slots and loaded from the system port at power-up time, and is authenticated in order to achieve PIPS 140-1 compliance.',
    #         'The retirement unit then extracts processed packets out of the retirement buffer in the same order that the chip originally received the packets, and outputs the processed packets.',
    #         'packet header information is sent to a packet classifier unit 204 where a classification engine rapidly determines security association information required for processing the packet,',
    #         'Strong ordering may be maintained in a number of ways, for example, by assigning a new packet to the next free cryptography processing unit in strict round-robin sequence. Packets are retired in the same sequence as units complete processing, thus ensuring order maintenance.',
    #         # 'Inbound packets ... if sequence check enabled for inbound, check & update sequence mask; update Engine scheduling status; mark packet descriptor as free; add back to free pool; II Schedule write.', # NOTE this fails because there is a chunk missing from the middle of the passage
    #         'Once in the system, a SAD lookup is conducted (660). Ifno matching SAD entry is found (662) one is created (664) in the IPSec Security Association Database. The packet is encapsulated (666), encrypted and authenticated (668). The encrypted packet is then sent out of the system (670).',
    #     ]

    #     parsed_patent_131 = parser.parse_patent_from_pdf_path(self.patent_131_path)

    #     citations = []
    #     for passage in test_passages + test_passages_with_newlines_removed:
    #         # Will raise error if citation not found
    #         citations.append(utils.cite_passage(passage, parsed_patent_131))

    #     # "Many methods..." passage should have same citation line pair whether cited with newlines in or not
    #     self.assertEqual(citations[0], citations[3])

    #     self.assertEqual(
    #         [c[0].page_num for c in citations],
    #         [
    #             12,
    #             12,
    #             12,
    #             12,
    #             12,
    #             12,
    #             15,
    #             18,
    #             18,
    #             15,
    #             14,
    #             15,
    #             # 0,,
    #             18
    #         ]
    #     )

    #     for citation in citations:
    #         print(citation)
    #         print()