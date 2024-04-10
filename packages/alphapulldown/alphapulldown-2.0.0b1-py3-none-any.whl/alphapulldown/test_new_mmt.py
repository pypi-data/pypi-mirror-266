import pickle
from alphapulldown.utils.multimeric_template_utils import parse_mmcif_file
import shutil
from alphapulldown.utils.file_handlings import temp_fasta_file
from alphafold.data import parsers
from Bio.Align.Applications import ClustalwCommandline
import tempfile
from Bio import AlignIO
from alphafold.data.templates import (_build_query_to_hit_index_mapping,
                                      _extract_template_features)
from typing import Optional
from alphafold.data.tools import kalign


def obtain_kalign_binary_path() -> Optional[str]:
    assert shutil.which('kalign') is not None, "Could not find kalign in your environment"
    return shutil.which('kalign')
aligner = kalign.Kalign(binary_path = obtain_kalign_binary_path())
chain_id = 'A'
p03496 = pickle.load(open("/g/alphafold/flu/af2.3_screening_features/P03496.pkl",'rb'))
mmcif_file_path = '/g/kosinski/geoffrey/alphapulldown/truemultimer_example/3L4Q.cif'
parse_result = parse_mmcif_file('3l4q',mmcif_file_path,chain_id=chain_id)
parsed_mmcif_object = parse_result.mmcif_object
parsed_resseq = parsed_mmcif_object.chain_to_seqres[chain_id]

sequence_str = f">query\n{p03496.sequence}\n>template_hit\n{parsed_resseq}"
parsed_a3m = parsers.parse_a3m(aligner.align([p03496.sequence,parsed_resseq]))
aligned_query, aligned_template_hit = parsed_a3m.sequences

with temp_fasta_file(sequence_str) as fasta_file, tempfile.TemporaryDirectory() as temp_dir:
    aligned_fasta_file = f"{temp_dir}/fake_alignment.aln"
    msa_aligner = ClustalwCommandline(cmd=shutil.which('clustalw'), 
                                  infile=fasta_file,
                                  output='clustal', outfile=aligned_fasta_file)
    msa_aligner()
    alignments = AlignIO.read(aligned_fasta_file,format='clustal')
    for alignment in alignments:
        if alignment.id != 'query':
            template_hit_seq = str(alignment.seq)
            hit_indices = parsers._get_indices(template_hit_seq,start=0)
        else:
            query_sequence = str(alignment.seq)
            query_indecies = parsers._get_indices(query_sequence,start=0)

original_query_sequence = p03496.sequence

mapping = _build_query_to_hit_index_mapping(query_sequence, 
                                            template_hit_seq, 
                                            hit_indices, 
                                            query_indecies,original_query_sequence)

for k,v in mapping.items():
    print(f"{original_query_sequence[k]} is mapped to {parsed_resseq[v]}")
print(f"aligned query:\n{query_sequence} and aligned template:\n{template_hit_seq}")


features, realign_warning = _extract_template_features(
                mmcif_object = parse_result.mmcif_object,
                pdb_id = "test",
                mapping = mapping,
                template_sequence = template_hit_seq.replace("-",''),
                query_sequence = original_query_sequence,
                template_chain_id = chain_id,
                kalign_binary_path = obtain_kalign_binary_path()
            )
 